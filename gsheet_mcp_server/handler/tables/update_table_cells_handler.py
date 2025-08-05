"""Handler for updating multiple cells in tables in Google Sheets."""

from typing import List, Dict, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    validate_cell_value
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_table_cells_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    cell_updates: List[Dict[str, Union[str, int, float, bool, None]]]
) -> str:
    """
    Update multiple cells in a table in Google Sheets using the official updateCells operation.
    
    According to the official Google Sheets API documentation, to update multiple cells in a table:
    1. Use UpdateCellsRequest to update specific cells with their values
    2. Apply proper formatting based on column types
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        cell_updates: List of cell updates, each containing:
            - row_index: Row index (1-based, excluding header)
            - column_index: Column index (1-based)
            - value: New value for the cell
    
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
        
        if not cell_updates or not isinstance(cell_updates, list):
            return compact_json_response({
                "success": False,
                "message": "Cell updates are required and must be a list."
            })
        
        # Validate cell updates structure
        validated_updates = []
        invalid_updates = []
        
        for i, update in enumerate(cell_updates):
            if not isinstance(update, dict):
                invalid_updates.append({"index": i, "error": "Update must be a dictionary"})
                continue
            
            row_index: Union[int, None] = update.get("row_index")
            column_index: Union[int, None] = update.get("column_index")
            value: Union[str, int, float, bool, None] = update.get("value")
            
            if not isinstance(row_index, int) or row_index < 1:
                invalid_updates.append({"index": i, "error": "row_index must be a positive integer"})
                continue
            
            if not isinstance(column_index, int) or column_index < 1:
                invalid_updates.append({"index": i, "error": "column_index must be a positive integer"})
                continue
            
            # Validate cell value
            value_validation = validate_cell_value(value)
            if not value_validation["valid"]:
                invalid_updates.append({"index": i, "error": value_validation["error"]})
                continue
            
            validated_updates.append({
                "row_index": row_index,
                "column_index": column_index,
                "value": value_validation["cleaned_value"]
            })
        
        if invalid_updates:
            error_messages = [f"Update {item['index']+1}: {item['error']}" for item in invalid_updates]
            return compact_json_response({
                "success": False,
                "message": f"Invalid cell updates: {'; '.join(error_messages)}",
                "invalid_updates": invalid_updates
            })
        
        if not validated_updates:
            return compact_json_response({
                "success": False,
                "message": "No valid cell updates provided after validation."
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
        
        # Validate cell positions are within table range
        valid_cell_updates = []
        out_of_range_updates = []
        
        for update in validated_updates:
            row_index = update["row_index"]
            column_index = update["column_index"]
            
            # Convert 1-based user indices to 0-based API indices
            api_row_index = table_start_row + row_index
            api_col_index = table_start_col + column_index - 1  # Column index is 1-based
            
            if (api_row_index < table_start_row or api_row_index >= table_end_row or
                api_col_index < table_start_col or api_col_index >= table_end_col):
                out_of_range_updates.append({
                    "row_index": row_index,
                    "column_index": column_index,
                    "error": f"Cell position ({row_index}, {column_index}) is outside table range"
                })
            else:
                valid_cell_updates.append({
                    "api_row_index": api_row_index,
                    "api_col_index": api_col_index,
                    "value": update["value"],
                    "user_row_index": row_index,
                    "user_col_index": column_index
                })
        
        if out_of_range_updates:
            error_messages = [f"({item['row_index']}, {item['column_index']}): {item['error']}" for item in out_of_range_updates]
            return compact_json_response({
                "success": False,
                "message": f"Out of range cell updates: {'; '.join(error_messages)}",
                "out_of_range_updates": out_of_range_updates
            })
        
        if not valid_cell_updates:
            return compact_json_response({
                "success": False,
                "message": "No valid cell updates after range validation."
            })
        
        # Create batch update requests for all valid cells
        requests = []
        
        for cell_update in valid_cell_updates:
            # Get column type for proper formatting
            column_type = "TEXT"  # Default type
            col_index = cell_update["user_col_index"] - 1  # Convert to 0-based
            if col_index < len(columns):
                column_type = columns[col_index].get("type", "TEXT")
            
            # Create cell data with proper formatting
            cell_value = cell_update["value"]
            if cell_value is None:
                cell_data = {"userEnteredValue": {"stringValue": ""}}
            elif isinstance(cell_value, bool):
                cell_data = {"userEnteredValue": {"boolValue": cell_value}}
            elif isinstance(cell_value, (int, float)):
                cell_data = {"userEnteredValue": {"numberValue": float(cell_value)}}
            else:
                cell_data = {"userEnteredValue": {"stringValue": str(cell_value)}}
            
            # Create updateCells request for this cell
            update_request = {
                "updateCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": cell_update["api_row_index"],
                        "endRowIndex": cell_update["api_row_index"] + 1,
                        "startColumnIndex": cell_update["api_col_index"],
                        "endColumnIndex": cell_update["api_col_index"] + 1
                    },
                    "rows": [{"values": [cell_data]}],
                    "fields": "userEnteredValue,userEnteredFormat"
                }
            }
            requests.append(update_request)
        
        # Execute the batch update
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        updated_cells = len(replies)
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "cells_updated": updated_cells,
            "total_updates_requested": len(validated_updates),
            "message": f"Successfully updated {updated_cells} cell(s) in table '{table_name}' in '{sheet_name}'"
        }
        
        return compact_json_response(response_data)
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error updating table cells: {str(e)}"
        }) 