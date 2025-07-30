"""
Handler for deleting records from native Google Sheets tables.

This module provides functionality to delete specific records from existing table objects.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name
from ..helper.sheets_utils import get_sheet_ids_by_names
from ..helper.tables_utils import get_table_info, get_table_ids_by_names
from ..helper.json_utils import compact_json_response


class DeleteTableRecordsRequest(BaseModel):
    """Request model for deleting records from native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to delete records from")
    row_indices: List[int] = Field(..., description="List of row indices to delete (0-based, relative to table data rows, excluding header)")
    delete_type: str = Field(default="ROWS", description="Type of deletion: ROWS (delete entire rows) or CLEAR (clear cell contents only)")


def delete_table_records(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    row_indices: List[int],
    delete_type: str = "ROWS"
) -> str:
    """
    Delete records from a native Google Sheets table.
    
    This tool deletes specific records from an existing table:
    - Validates row indices are within table bounds
    - Supports two deletion types: ROWS (delete entire rows) or CLEAR (clear contents only)
    - Updates table range to reflect the changes
    - Maintains table integrity
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete records from
        row_indices: List of row indices to delete (0-based, relative to table data rows, excluding header)
        delete_type: Type of deletion ("ROWS" or "CLEAR")
    
    Returns:
        Compact JSON string containing operation results with table information
        
    Raises:
        RuntimeError: If record deletion fails
    """
    try:
        # Validate delete type
        if delete_type not in ["ROWS", "CLEAR"]:
            return compact_json_response({
                "success": False,
                "message": "Delete type must be 'ROWS' or 'CLEAR'"
            })
        
        # Validate row indices
        if not row_indices:
            return compact_json_response({
                "success": False,
                "message": "At least one row index must be specified"
            })
        
        for row_idx in row_indices:
            if row_idx < 0:
                return compact_json_response({
                    "success": False,
                    "message": f"Row index {row_idx} must be >= 0"
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
        current_row_count = table_info.get("row_count", 0)
        data_row_count = current_row_count - 1  # Exclude header row
        
        print(f"DEBUG: Current table info before deleting records:")
        print(f"  Table: {table_name}")
        print(f"  Current row count: {current_row_count}")
        print(f"  Data row count: {data_row_count}")
        print(f"  Table range: {table_range}")
        print(f"  Requested row indices: {row_indices}")
        print(f"  Delete type: {delete_type}")
        
        # Validate row indices are within table bounds
        for row_idx in row_indices:
            if row_idx >= data_row_count:
                return compact_json_response({
                    "success": False,
                    "message": f"Row index {row_idx} is out of range. Valid range: 0 to {data_row_count - 1}"
                })
        
        # Sort row indices in descending order to avoid index shifting issues
        sorted_row_indices = sorted(row_indices, reverse=True)
        
        # Calculate actual row positions in sheet (add 1 to skip header row)
        actual_row_positions = [table_range.get("startRowIndex", 0) + 1 + row_idx for row_idx in sorted_row_indices]
        
        if delete_type == "ROWS":
            # Delete entire rows using deleteDimension
            requests = []
            for row_pos in actual_row_positions:
                requests.append({
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": row_pos,
                            "endIndex": row_pos + 1
                        }
                    }
                })
            
            # Execute delete requests
            delete_request = {"requests": requests}
            print(f"DEBUG: Deleting rows at positions: {actual_row_positions}")
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=delete_request
            ).execute()
            
            # Update table range to reflect deleted rows (with error handling)
            deleted_count = len(sorted_row_indices)
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
                                            "endRowIndex": table_range.get("endRowIndex", 0) - deleted_count,
                                            "startColumnIndex": table_range.get("startColumnIndex", 0),
                                            "endColumnIndex": table_range.get("endColumnIndex", 0)
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
            
        else:  # CLEAR
            # Clear cell contents only
            clear_ranges = []
            for row_pos in actual_row_positions:
                # Clear the entire row range within the table
                start_col = table_range.get("startColumnIndex", 0)
                end_col = table_range.get("endColumnIndex", 0)
                clear_ranges.append(f"{sheet_name}!{chr(65 + start_col)}{row_pos + 1}:{chr(65 + end_col - 1)}{row_pos + 1}")
            
            # Execute clear requests
            for clear_range in clear_ranges:
                sheets_service.spreadsheets().values().clear(
                    spreadsheetId=spreadsheet_id,
                    range=clear_range
                ).execute()
            
            print(f"DEBUG: Cleared contents for rows at positions: {actual_row_positions}")
        
        # Get updated table info
        updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        new_row_count = updated_table_info.get("row_count", current_row_count - len(sorted_row_indices) if delete_type == "ROWS" else current_row_count)
        
        print(f"DEBUG: Updated table info after deleting records:")
        print(f"  New row count: {new_row_count}")
        print(f"  Updated table range: {updated_table_info.get('range', {})}")
        
        # Prepare response message
        operation_text = "deleted" if delete_type == "ROWS" else "cleared"
        rows_text = f"{len(sorted_row_indices)} row(s)" if len(sorted_row_indices) > 1 else f"row {sorted_row_indices[0]}"
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": table_id,
            "deleted_row_indices": sorted_row_indices,
            "actual_row_positions": actual_row_positions,
            "delete_type": delete_type,
            "rows_affected": len(sorted_row_indices),
            "new_row_count": new_row_count,
            "updated_table_info": updated_table_info,
            "message": f"Successfully {operation_text} {rows_text} from table '{table_name}'"
        })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        return compact_json_response({
            "success": False,
            "message": f"Error deleting table records: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error deleting table records: {error}"
        })





 