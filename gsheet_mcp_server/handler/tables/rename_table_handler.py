"""Handler for renaming tables in Google Sheets."""

from typing import List, Any, Dict
from googleapiclient.errors import HttpError
import re
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response


def rename_table_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    old_table_name: str,
    new_table_name: str
) -> str:
    """
    Rename a table in a Google Spreadsheet.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        old_table_name: Current name of the table to rename
        new_table_name: New name for the table
    
    Returns:
        str: Success message with table details
    """
    try:
        # Validate inputs
        if not old_table_name or old_table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Old table name is required and cannot be empty."
            })
        
        if not new_table_name or new_table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "New table name is required and cannot be empty."
            })
        
        # Clean and validate new table name
        new_table_name = _clean_table_name(new_table_name)
        if not new_table_name:
            return compact_json_response({
                "success": False,
                "message": "Invalid new table name. Please provide a valid name."
            })
        
        # Check if old and new names are the same
        if old_table_name.strip() == new_table_name:
            return compact_json_response({
                "success": False,
                "message": f"New table name '{new_table_name}' is the same as the old name '{old_table_name}'."
            })
        
        # Get spreadsheet ID using utility function
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })

        # Get sheet ID using utility function
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
            })
        
        # Get old table ID
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [old_table_name])
        old_table_id = table_ids.get(old_table_name)
        if not old_table_id:
            return compact_json_response({
                "success": False,
                "message": f"Table '{old_table_name}' not found in sheet '{sheet_name}'."
            })
        
        # Check if new table name already exists
        existing_table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [new_table_name])
        if existing_table_ids.get(new_table_name):
            return compact_json_response({
                "success": False,
                "message": f"Table with name '{new_table_name}' already exists in sheet '{sheet_name}'."
            })
        
        # Create update table request
        update_request = {
            "updateTable": {
                "table": {
                    "tableId": old_table_id,
                    "name": new_table_name
                },
                "fields": "name"
            }
        }
        
        # Prepare batch update request
        batch_request = {
            "requests": [update_request]
        }
        
        # Execute batch update
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_request
        ).execute()
        
        return compact_json_response({
            "success": True,
            "message": f"Successfully renamed table from '{old_table_name}' to '{new_table_name}' in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'.",
            "data": {
                "old_table_name": old_table_name,
                "new_table_name": new_table_name,
                "sheet_name": sheet_name,
                "spreadsheet_name": spreadsheet_name
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error renaming table: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        })


def _clean_table_name(table_name: str) -> str:
    """
    Clean and validate table name for Google Sheets.
    
    Args:
        table_name: Raw table name from user
        
    Returns:
        str: Cleaned table name or empty string if invalid
    """
    import re
    
    if not table_name:
        return ""
    
    # Remove leading/trailing whitespace
    table_name = table_name.strip()
    
    if not table_name:
        return ""
    
    # Remove invalid characters (only allow letters, numbers, spaces, hyphens, underscores)
    # Replace invalid characters with spaces
    table_name = re.sub(r'[^a-zA-Z0-9\s\-_]', ' ', table_name)
    
    # Replace multiple spaces with single space
    table_name = re.sub(r'\s+', ' ', table_name)
    
    # Remove leading/trailing spaces again
    table_name = table_name.strip()
    
    # Ensure it starts with a letter or number
    if not re.match(r'^[a-zA-Z0-9]', table_name):
        return ""
    
    # Limit length to 50 characters
    if len(table_name) > 50:
        table_name = table_name[:50].strip()
    
    # If it's just "table" or similar generic names, make it more descriptive
    if table_name.lower() in ['table', 'new table', 'untitled']:
        table_name = f"Table"
    
    return table_name
