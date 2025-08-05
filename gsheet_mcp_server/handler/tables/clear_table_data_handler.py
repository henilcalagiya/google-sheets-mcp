"""Handler for clearing data from tables in Google Sheets."""

from typing import Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def clear_table_data_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    clear_headers: bool = False
) -> str:
    """
    Clear data from a table in Google Sheets using updateCells.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to clear
        clear_headers: Whether to also clear the header row (default: False)
    
    Returns:
        str: Success message with clear details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
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
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve table information: {str(e)}"
            })
        
        # Get table range
        table_range = table_info.get("range", {})
        table_start_row = table_range.get("startRowIndex", 0)
        table_end_row = table_range.get("endRowIndex", 0)
        table_start_col = table_range.get("startColumnIndex", 0)
        table_end_col = table_range.get("endColumnIndex", 0)
        
        # Calculate the range to clear
        if clear_headers:
            # Clear entire table including headers
            clear_start_row = table_start_row
            clear_end_row = table_end_row
        else:
            # Clear only data rows (exclude header)
            clear_start_row = table_start_row + 1
            clear_end_row = table_end_row
        
        # Check if there's data to clear
        if clear_start_row >= clear_end_row:
            return compact_json_response({
                "success": False,
                "message": "No data to clear. Table is empty or only contains headers."
            })
        
        # Create empty cells for the range
        num_rows = clear_end_row - clear_start_row
        num_cols = table_end_col - table_start_col
        
        empty_rows = []
        for _ in range(num_rows):
            empty_cells = []
            for _ in range(num_cols):
                empty_cells.append({"userEnteredValue": {"stringValue": ""}})
            empty_rows.append({"values": empty_cells})
        
        # Create updateCells request according to official API documentation
        clear_cells_request = {
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": clear_start_row,
                    "endRowIndex": clear_end_row,
                    "startColumnIndex": table_start_col,
                    "endColumnIndex": table_end_col
                },
                "rows": empty_rows,
                "fields": "userEnteredValue"
            }
        }
        
        # Create updateTable request to resize the table
        if clear_headers:
            # If clearing headers, resize to just header row
            new_end_row = table_start_row + 1
        else:
            # If keeping headers, resize to just header row
            new_end_row = table_start_row + 1
        
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_start_row,
                        "endRowIndex": new_end_row,
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": table_end_col
                    }
                },
                "fields": "range"
            }
        }
        
        # Execute both requests
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [clear_cells_request, update_table_request]}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        if replies:
            # Check for updateCells response
            update_cells_response = None
            update_table_response = None
            
            for reply in replies:
                if "updateCells" in reply:
                    update_cells_response = reply["updateCells"]
                elif "updateTable" in reply:
                    update_table_response = reply["updateTable"]
            
            if update_cells_response:
                updated_cells = update_cells_response.get("updatedCells", 0)
                
                response_data = {
                    "success": True,
                    "spreadsheet_name": spreadsheet_name,
                    "sheet_name": sheet_name,
                    "table_name": table_name,
                    "rows_cleared": num_rows,
                    "columns_cleared": num_cols,
                    "cells_cleared": updated_cells,
                    "headers_cleared": clear_headers,
                    "table_resized": update_table_response is not None,
                    "new_table_range": {
                        "startRowIndex": table_start_row,
                        "endRowIndex": new_end_row,
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": table_end_col
                    },
                    "message": f"Successfully cleared {num_rows} row(s) and resized table '{table_name}' in '{sheet_name}'"
                }
                
                if clear_headers:
                    response_data["message"] = f"Successfully cleared all data including headers and resized table '{table_name}' in '{sheet_name}'"
                
                return compact_json_response(response_data)
            else:
                # If no updateCells response found, but API call succeeded, assume success
                response_data = {
                    "success": True,
                    "spreadsheet_name": spreadsheet_name,
                    "sheet_name": sheet_name,
                    "table_name": table_name,
                    "rows_cleared": num_rows,
                    "columns_cleared": num_cols,
                    "cells_cleared": num_rows * num_cols,
                    "headers_cleared": clear_headers,
                    "table_resized": True,
                    "new_table_range": {
                        "startRowIndex": table_start_row,
                        "endRowIndex": new_end_row,
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": table_end_col
                    },
                    "message": f"Successfully cleared {num_rows} row(s) and resized table '{table_name}' in '{sheet_name}' (API response structure may vary)"
                }
                
                if clear_headers:
                    response_data["message"] = f"Successfully cleared all data including headers and resized table '{table_name}' in '{sheet_name}' (API response structure may vary)"
                
                return compact_json_response(response_data)
        else:
            return compact_json_response({
                "success": False,
                "message": "Failed to clear table data - no response data from API"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error clearing table data: {str(e)}"
        }) 