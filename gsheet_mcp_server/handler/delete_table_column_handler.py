"""
Handler for deleting columns from native Google Sheets tables.

This module provides functionality to delete columns from existing table objects.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name
from ..helper.sheets_utils import get_sheet_ids_by_names
from ..helper.tables_utils import get_table_info, get_table_ids_by_names
from ..helper.json_utils import compact_json_response


class DeleteTableColumnRequest(BaseModel):
    """Request model for deleting columns from native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to delete column from")
    column_index: int = Field(..., description="Index of the column to delete (0-based)")


def delete_table_column(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_index: int
) -> str:
    """
    Delete a column from a native Google Sheets table.
    
    This tool deletes a specific column from an existing table:
    - Validates column index is within table bounds
    - Removes the column using deleteDimension
    - Updates table range to reflect the change
    - Maintains table integrity
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete column from
        column_index: Index of the column to delete (0-based)
    
    Returns:
        Compact JSON string containing operation results with table information
        
    Raises:
        RuntimeError: If column deletion fails
    """
    try:
        # Validate column index
        if column_index < 0:
            return compact_json_response({
                "success": False,
                "message": "Column index must be >= 0"
            })
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found"
            })
        
        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'"
            })
        
        # Get table ID and info
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [table_name])
        table_id = table_ids.get(table_name)
        if not table_id:
            return compact_json_response({
                "success": False,
                "message": f"Table '{table_name}' not found in sheet '{sheet_name}'"
            })
        
        # Get current table information
        table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        table_range = table_info.get("range", {})
        current_column_count = table_info.get("column_count", 0)
        
        print(f"DEBUG: Current table info before deleting column:")
        print(f"  Table: {table_name}")
        print(f"  Current column count: {current_column_count}")
        print(f"  Table range: {table_range}")
        print(f"  Requested column index: {column_index}")
        
        # Validate column index is within table bounds
        if column_index >= current_column_count:
            return compact_json_response({
                "success": False,
                "message": f"Column index {column_index} is out of range. Valid range: 0 to {current_column_count - 1}"
            })
        
        # Calculate actual column position in sheet
        target_col_index = table_range.get("startColumnIndex", 0) + column_index
        
        # Get column header before deletion for response
        header_range = f"{sheet_name}!{chr(65 + target_col_index)}1"
        try:
            header_response = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=header_range
            ).execute()
            column_header = header_response.get("values", [[""]])[0][0] if header_response.get("values") else "Unknown"
        except:
            column_header = f"Column {column_index}"
        
        # Step 1: Delete the column using deleteDimension
        delete_request = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": target_col_index,
                            "endIndex": target_col_index + 1
                        }
                    }
                }
            ]
        }
        
        print(f"DEBUG: Deleting column at index {target_col_index} (column {column_index})")
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=delete_request
        ).execute()
        
        # Step 2: Update table range to reflect the deleted column (with error handling)
        try:
            update_table_request = {
                "requests": [
                    {
                        "updateTable": {
                            "tableId": table_id,
                            "table": {
                                "tableProperties": {
                                    "range": {
                                        "startRowIndex": table_range.get("startRowIndex", 0),
                                        "endRowIndex": table_range.get("endRowIndex", 0),
                                        "startColumnIndex": table_range.get("startColumnIndex", 0),
                                        "endColumnIndex": table_range.get("endColumnIndex", 0) - 1
                                    }
                                }
                            }
                        }
                    }
                ]
            }
            
            print(f"DEBUG: Updating table range with request: {update_table_request}")
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=update_table_request
            ).execute()
            print(f"DEBUG: Table range update completed")
            
        except Exception as e:
            print(f"DEBUG: Warning - could not update table range: {e}")
            # Continue anyway as deleteDimension should handle it
        
        # Get updated table info
        updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        new_column_count = updated_table_info.get("column_count", current_column_count - 1)
        
        print(f"DEBUG: Updated table info after deleting column:")
        print(f"  New column count: {new_column_count}")
        print(f"  Updated table range: {updated_table_info.get('range', {})}")
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": table_id,
            "deleted_column_index": column_index,
            "deleted_column_header": column_header,
            "target_column_index": target_col_index,
            "new_column_count": new_column_count,
            "updated_table_info": updated_table_info,
            "message": f"Successfully deleted column '{column_header}' (index {column_index}) from table '{table_name}'"
        })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        return compact_json_response({
            "success": False,
            "message": f"Error deleting table column: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error deleting table column: {error}"
        })





 