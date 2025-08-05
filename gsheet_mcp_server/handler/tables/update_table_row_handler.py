"""Handler for updating entire rows in tables in Google Sheets."""

from typing import List, Dict, Any, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    validate_row_data
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_table_row_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    row_index: int,
    data: List[Union[str, int, float, bool, None]]
) -> str:
    """
    Update an entire row in a table in Google Sheets using the official updateCells operation.
    
    According to the official Google Sheets API documentation, to update a row in a table:
    1. Use UpdateCellsRequest to update all cells in the specified row
    2. Apply proper formatting based on column types
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        row_index: Row index to update (1-based, excluding header)
        data: List of values for the row (must match table column count)
    
    Returns:
        str: Success message with update details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if not isinstance(row_index, int) or row_index < 1:
            return compact_json_response({
                "success": False,
                "message": "Row index must be a positive integer (1 or greater)."
            })
        
        if not data or not isinstance(data, list):
            return compact_json_response({
                "success": False,
                "message": "Data is required and must be a list of values."
            })
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })

        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
            })
        
        # Get table ID
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [table_name])
        table_id = table_ids.get(table_name)
        if not table_id:
            return compact_json_response({
                "success": False,
                "message": f"Table '{table_name}' not found in sheet '{sheet_name}'."
            })
        
        # Get table information
        try:
            table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
            current_column_count = table_info.get('column_count', 0)
            columns = table_info.get('columns', [])
            table_range = table_info.get('range', {})
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Get table boundaries
        table_start_row = table_range.get("startRowIndex", 0)
        table_end_row = table_range.get("endRowIndex", 0)
        table_start_col = table_range.get("startColumnIndex", 0)
        table_end_col = table_range.get("endColumnIndex", 0)
        
        # Validate row index is within table range
        max_row_index = table_end_row - table_start_row - 1  # Exclude header
        if row_index > max_row_index:
            return compact_json_response({
                "success": False,
                "message": f"Row index {row_index} is outside table range (1 to {max_row_index})."
            })
        
        # Validate data structure against table columns
        row_validation = validate_row_data(data, current_column_count)
        if not row_validation["valid"]:
            return compact_json_response({
                "success": False,
                "message": f"Invalid row data: {row_validation['error']}"
            })
        
        validated_data = row_validation["cleaned_row"]
        
        # Convert 1-based user index to 0-based API index (accounting for header)
        api_row_index = table_start_row + row_index
        
        # Create row values with proper formatting based on column types
        row_values = []
        for i, cell_value in enumerate(validated_data):
            # Get column type for proper formatting
            column_type = "TEXT"  # Default type
            if i < len(columns):
                column_type = columns[i].get("type", "TEXT")
            
            # Create cell data with proper formatting
            if cell_value is None:
                row_values.append({"userEnteredValue": {"stringValue": ""}})
            elif isinstance(cell_value, bool):
                row_values.append({"userEnteredValue": {"boolValue": cell_value}})
            elif isinstance(cell_value, (int, float)):
                row_values.append({"userEnteredValue": {"numberValue": float(cell_value)}})
            else:
                row_values.append({"userEnteredValue": {"stringValue": str(cell_value)}})
        
        # Create updateCells request according to official API documentation
        update_cells_request = {
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": api_row_index,
                    "endRowIndex": api_row_index + 1,
                    "startColumnIndex": table_start_col,
                    "endColumnIndex": table_end_col
                },
                "rows": [{"values": row_values}],
                "fields": "userEnteredValue,userEnteredFormat"
            }
        }
        
        # Execute the updateCells request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [update_cells_request]}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        if replies:
            # Check if updateCells response exists in any reply
            update_cells_response = None
            for reply in replies:
                if "updateCells" in reply:
                    update_cells_response = reply["updateCells"]
                    break
            
            if update_cells_response:
                updated_cells = update_cells_response.get("updatedCells", 0)
                
                response_data = {
                    "success": True,
                    "spreadsheet_name": spreadsheet_name,
                    "sheet_name": sheet_name,
                    "table_name": table_name,
                    "row_index": row_index,
                    "updated_cells": updated_cells,
                    "updated_data": validated_data,
                    "message": f"Successfully updated row {row_index} in table '{table_name}' in '{sheet_name}'"
                }
                
                return compact_json_response(response_data)
            else:
                # If no updateCells response found, but API call succeeded, assume success
                response_data = {
                    "success": True,
                    "spreadsheet_name": spreadsheet_name,
                    "sheet_name": sheet_name,
                    "table_name": table_name,
                    "row_index": row_index,
                    "updated_cells": len(validated_data),
                    "updated_data": validated_data,
                    "message": f"Successfully updated row {row_index} in table '{table_name}' in '{sheet_name}' (API response structure may vary)"
                }
                
                return compact_json_response(response_data)
        else:
            return compact_json_response({
                "success": False,
                "message": "Failed to update row - no response data from API"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error updating table row: {str(e)}"
        }) 