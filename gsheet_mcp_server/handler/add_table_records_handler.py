"""
Handler for appending cells to native Google Sheets tables using AppendCellsRequest.

This module provides functionality to add new cells/data to existing table objects.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name
from ..helper.sheets_utils import get_sheet_ids_by_names
from ..helper.tables_utils import get_table_info, get_table_ids_by_names
from ..helper.json_utils import compact_json_response


class AddTableRecordsRequest(BaseModel):
    """Request model for appending/inserting records to native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to append/insert records to")
    data: List[List[str]] = Field(..., description="2D list of data rows to append/insert")
    operation: str = Field(default="APPEND", description="Operation type: APPEND or INSERT")
    position: int = Field(default=None, description="Position to insert data (0-based, required for INSERT operation)")
    append_position: str = Field(default="END", description="Where to append: START or END (for APPEND operation)")


def add_table_records(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    data: List[List[str]],
    operation: str = "APPEND",
    position: int = None,
    append_position: str = "END"
) -> str:
    """
    Add records to a native Google Sheets table using a simplified, unified approach.
    
    This tool uses a single, reliable pattern:
    1. Get table information and current data
    2. Calculate new data positions
    3. Insert rows if needed (for INSERT operations)
    4. Write data to calculated positions
    5. Let Google Sheets handle table range updates automatically
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add records to
        data: 2D list of data rows to add
        operation: Operation type ("APPEND" or "INSERT")
        position: Position to insert data (0-based, required for INSERT)
        append_position: Where to append (START or END, for APPEND operation)
    
    Returns:
        Compact JSON string containing operation results with table information
        
    Raises:
        RuntimeError: If table operation fails
    """
    try:
        # Validate operation and parameters
        if operation not in ["APPEND", "INSERT"]:
            return compact_json_response({
                "success": False,
                "message": "Operation must be 'APPEND' or 'INSERT'"
            })
        
        if operation == "INSERT" and position is None:
            return compact_json_response({
                "success": False,
                "message": "Position is required for INSERT operation"
            })
        
        if operation == "INSERT" and position < 0:
            return compact_json_response({
                "success": False,
                "message": "Position must be >= 0 for INSERT operation"
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
        
        # Get table ID from table name
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
        
        print(f"DEBUG: Current table info before operation:")
        print(f"  Table: {table_name}")
        print(f"  Current row count: {current_row_count}")
        print(f"  Table range: {table_range}")
        print(f"  Start row: {table_info.get('start_row', 0)}, End row: {table_info.get('end_row', 0)}")
        
        # Calculate target positions based on operation
        if operation == "APPEND":
            if append_position == "END":
                # Append to end: insert after the last data row
                target_start_row = table_range.get("endRowIndex", 0)
            else:  # START
                # Append to start: insert after header row
                target_start_row = table_range.get("startRowIndex", 0) + 1
        else:  # INSERT
            # Insert at specific position: calculate actual sheet position
            target_start_row = table_range.get("startRowIndex", 0) + 1 + position
        
        # Convert data to simple values
        values = []
        for row in data:
            row_values = []
            for cell_value in row:
                # Convert to appropriate type
                if isinstance(cell_value, (int, float)):
                    row_values.append(cell_value)
                elif isinstance(cell_value, bool):
                    row_values.append(cell_value)
                else:
                    row_values.append(str(cell_value))
            values.append(row_values)
        
        # Step 1: Handle operations differently for better efficiency
        if operation == "APPEND":
            # For APPEND: Use values().append which is more efficient and handles table expansion
            range_name = f"{sheet_name}!A{target_start_row + 1}"
            
            print(f"DEBUG: Appending {len(values)} rows to table '{table_name}' at range {range_name}")
            
            # Use values().append for APPEND operations
            response = sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": values}
            ).execute()
            
            print(f"DEBUG: values().append response: {response}")
            
            # Explicitly update table range to ensure it's properly extended
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
                                            "endRowIndex": table_range.get("endRowIndex", 0) + len(values),
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
                # Continue anyway as values().append should handle it
            
        else:  # INSERT operation
            # For INSERT: Use values().update (simpler than batchUpdate with updateCells)
            range_name = f"{sheet_name}!A{target_start_row + 1}"
            
            # Insert empty rows first using insertDimension
            insert_request = {
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "ROWS",
                                "startIndex": target_start_row,
                                "endIndex": target_start_row + len(values)
                            },
                            "inheritFromBefore": True
                        }
                    }
                ]
            }
            
            # Execute the insert dimension request
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=insert_request
            ).execute()
            
            # Then write data using values().update (simpler than updateCells)
            response = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body={"values": values}
            ).execute()
        
        # Get updated table info to confirm changes
        updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        new_row_count = updated_table_info.get("row_count", current_row_count + len(values))
        
        print(f"DEBUG: Updated table info after operation:")
        print(f"  New row count: {new_row_count}")
        print(f"  Updated table range: {updated_table_info.get('range', {})}")
        print(f"  Start row: {updated_table_info.get('start_row', 0)}, End row: {updated_table_info.get('end_row', 0)}")
        
        # Prepare response message
        operation_text = "appended" if operation == "APPEND" else "inserted"
        position_text = f" at position {position}" if operation == "INSERT" else f" to {append_position.lower()}"
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": table_id,
            "operation": operation,
            "position": position if operation == "INSERT" else None,
            "append_position": append_position if operation == "APPEND" else None,
            "rows_affected": len(values),
            "new_row_count": new_row_count,
            "target_range": f"{sheet_name}!A{target_start_row + 1}:Z{target_start_row + len(values)}",
            "message": f"Successfully {operation_text} {len(values)} rows{position_text} in table '{table_name}'"
        })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        return compact_json_response({
            "success": False,
            "message": f"Error operating on table cells: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error operating on table cells: {error}"
        })





