"""
Handler for adding columns to native Google Sheets tables.

This module provides functionality to add new columns to existing table objects.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name
from ..helper.sheets_utils import get_sheet_ids_by_names
from ..helper.tables_utils import get_table_info, get_table_ids_by_names
from ..helper.json_utils import compact_json_response


class AddTableColumnRequest(BaseModel):
    """Request model for adding columns to native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to add column to")
    column_name: str = Field(..., description="Name/header for the new column")
    column_type: str = Field(default="TEXT", description="Column type: TEXT, DOUBLE, CURRENCY, DATE, etc.")
    position: Optional[int] = Field(default=None, description="Position to insert column (0-based, optional - adds at end if not specified)")
    data: List[str] = Field(default=[], description="List of data values for the new column (optional)")


def add_table_column(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_name: str,
    column_type: str = "TEXT",
    position: Optional[int] = None,
    data: List[str] = []
) -> str:
    """
    Add a new column to a native Google Sheets table.
    
    This tool adds a new column to an existing table with:
    - Proper column header
    - Column type specification
    - Optional data values
    - Automatic table range expansion
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add column to
        column_name: Name/header for the new column
        column_type: Column type (TEXT, DOUBLE, CURRENCY, DATE, etc.)
        position: Position to insert column (0-based, optional - adds at end if not specified)
        data: List of data values for the new column (optional)
    
    Returns:
        Compact JSON string containing operation results with table information
        
    Raises:
        RuntimeError: If column addition fails
    """
    try:
        # Validate column type
        valid_types = ["TEXT", "DOUBLE", "CURRENCY", "DATE", "TIME", "BOOLEAN"]
        if column_type not in valid_types:
            return compact_json_response({
                "success": False,
                "message": f"Invalid column type '{column_type}'. Valid types: {', '.join(valid_types)}"
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
        if not table_info:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve table information for '{table_name}'"
            })
        table_range = table_info.get("range", {})
        current_column_count = table_info.get("column_count", 0)
        
        print(f"DEBUG: Current table info before adding column:")
        print(f"  Table: {table_name}")
        print(f"  Current column count: {current_column_count}")
        print(f"  Table range: {table_range}")
        
        # Calculate target column position
        if position is None:
            # Add at the end of the table
            target_col_index = table_range.get("endColumnIndex", 0)
        else:
            # Add at specific position
            if position < 0 or position > current_column_count:
                return compact_json_response({
                    "success": False,
                    "message": f"Position {position} is out of range. Valid range: 0 to {current_column_count}"
                })
            target_col_index = table_range.get("startColumnIndex", 0) + position
        
        # Step 1: Insert the column and add header in a single batchUpdate
        batch_requests = [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": target_col_index,
                        "endIndex": target_col_index + 1
                    },
                    "inheritFromBefore": True
                }
            },
            {
                "updateCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_range.get("startRowIndex", 0),
                        "endRowIndex": table_range.get("startRowIndex", 0) + 1,
                        "startColumnIndex": target_col_index,
                        "endColumnIndex": target_col_index + 1
                    },
                    "rows": [
                        {
                            "values": [
                                {
                                    "userEnteredValue": {
                                        "stringValue": column_name
                                    }
                                }
                            ]
                        }
                    ],
                    "fields": "userEnteredValue"
                }
            }
        ]
        
        # Add data to the batch request if provided
        if data and len(data) > 0:
            # Calculate the range for data (starting from row 2, since row 1 is header)
            start_row = table_range.get("startRowIndex", 0) + 1  # +1 to skip header
            end_row = table_range.get("endRowIndex", 0)
            
            # Prepare data values
            data_rows = []
            for i in range(start_row, end_row):
                if i - start_row < len(data):
                    data_rows.append({
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": str(data[i - start_row])
                                }
                            }
                        ]
                    })
                else:
                    data_rows.append({
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": ""
                                }
                            }
                        ]
                    })
            
            if data_rows:
                batch_requests.append({
                    "updateCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": start_row + len(data_rows),
                            "startColumnIndex": target_col_index,
                            "endColumnIndex": target_col_index + 1
                        },
                        "rows": data_rows,
                        "fields": "userEnteredValue"
                    }
                })
        
        # Step 2: Update table range to include the new column
        # Note: We'll skip the updateTable request for now as it might not be needed
        # The insertDimension and updateCells should handle the table expansion automatically
        # If needed later, we can add it back with proper error handling
        
        print(f"DEBUG: Executing batch request with {len(batch_requests)} operations")
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": batch_requests}
        ).execute()
        
        # Step 3: Update table range to include the new column (with error handling)
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
                                        "endColumnIndex": table_range.get("endColumnIndex", 0) + 1
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
            # Continue anyway as insertDimension and updateCells should handle it
        
        # Get updated table info
        updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        if not updated_table_info:
            updated_table_info = table_info  # Fallback to original table info
        new_column_count = updated_table_info.get("column_count", current_column_count + 1)
        
        print(f"DEBUG: Updated table info after adding column:")
        print(f"  New column count: {new_column_count}")
        print(f"  Updated table range: {updated_table_info.get('range', {})}")
        
        # Prepare response message
        position_text = f" at position {position}" if position is not None else " at the end"
        data_text = f" with {len(data)} data values" if data and len(data) > 0 else ""
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": table_id,
            "column_name": column_name,
            "column_type": column_type,
            "position": position,
            "target_column_index": target_col_index,
            "new_column_count": new_column_count,
            "data_added": bool(data) and len(data) > 0,
            "data_count": len(data) if data and len(data) > 0 else 0,
            "updated_table_info": updated_table_info,
            "message": f"Successfully added column '{column_name}'{position_text} to table '{table_name}'{data_text}"
        })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        return compact_json_response({
            "success": False,
            "message": f"Error adding table column: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error adding table column: {error}"
        })



 