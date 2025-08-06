"""Handler for toggling table footers in Google Sheets."""

from typing import Dict, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def toggle_table_footer_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    action: str
) -> str:
    """
    Toggle table footer in Google Sheets using the official updateTable operation.
    
    This handler can add or remove a footer row from a table by updating the table range.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to toggle footer for
        action: Action to perform - "add" or "remove"
    
    Returns:
        str: Success message with toggle details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if action not in ["add", "remove"]:
            return compact_json_response({
                "success": False,
                "message": "Action must be 'add' or 'remove'."
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
            table_range = table_info.get('range', {})
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Extract current range information
        start_row_index = table_range.get('startRowIndex', 0)
        end_row_index = table_range.get('endRowIndex', 0)
        start_column_index = table_range.get('startColumnIndex', 0)
        end_column_index = table_range.get('endColumnIndex', 0)
        
        # Calculate new end row index based on action
        new_end_row_index = end_row_index
        if action == "add":
            new_end_row_index = end_row_index + 1
        elif action == "remove":
            new_end_row_index = end_row_index - 1
        
        # Validate that we're not removing more rows than we have
        if action == "remove" and new_end_row_index <= start_row_index:
            return compact_json_response({
                "success": False,
                "message": "Cannot remove footer: table would have no data rows."
            })
        
        # Create batch update requests
        requests = []
        
        # Update table range
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row_index,
                        "endRowIndex": new_end_row_index,
                        "startColumnIndex": start_column_index,
                        "endColumnIndex": end_column_index
                    }
                },
                "fields": "range"
            }
        }
        requests.append(update_table_request)
        
        # Execute the batch update
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        
        # Prepare response data
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "action": action,
            "old_range": {
                "startRowIndex": start_row_index,
                "endRowIndex": end_row_index,
                "startColumnIndex": start_column_index,
                "endColumnIndex": end_column_index
            },
            "new_range": {
                "startRowIndex": start_row_index,
                "endRowIndex": new_end_row_index,
                "startColumnIndex": start_column_index,
                "endColumnIndex": end_column_index
            },
            "message": f"Successfully {action}ed footer for table '{table_name}' in '{sheet_name}'"
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
            "message": f"Error toggling table footer: {str(e)}"
        }) 