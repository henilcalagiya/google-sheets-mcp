"""Handler for updating table titles in Google Sheets."""

from typing import Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    validate_table_name,
    get_table_ids_by_names,
    check_duplicate_table_name
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_table_title_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    old_table_name: str,
    new_table_name: str
) -> str:
    """
    Update a table title in Google Sheets using the Google Sheets API updateTable request.
    
    This function validates inputs, checks for duplicates, and performs the update operation
    while preserving all other table properties (range, columns, data validation, etc.).
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        old_table_name: Current name of the table to update
        new_table_name: New title for the table
    
    Returns:
        JSON string with success status and update details
    """
    try:
        # Validate old table name
        if not old_table_name or old_table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Old table name is required."
            })
        
        validated_old_table_name = old_table_name.strip()
        
        # Validate new table name
        if not new_table_name or new_table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "New table title is required."
            })
        
        new_table_validation = validate_table_name(new_table_name)
        if not new_table_validation["valid"]:
            return compact_json_response({
                "success": False,
                "message": new_table_validation["error"]
            })
        
        validated_new_table_name = new_table_validation["cleaned_name"]
        
        # Check if old and new names are the same
        if validated_old_table_name == validated_new_table_name:
            return compact_json_response({
                "success": False,
                "message": "Old and new table titles are the same."
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
        
        # Get table ID for the old table name
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [validated_old_table_name])
        table_id = table_ids.get(validated_old_table_name)
        
        if table_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Table '{validated_old_table_name}' not found in sheet '{sheet_name}'."
            })
        
        # Check for duplicate new table name (excluding the table being updated)
        duplicate_check = check_duplicate_table_name(sheets_service, spreadsheet_id, sheet_name, validated_new_table_name)
        if duplicate_check["has_duplicate"]:
            return compact_json_response({
                "success": False,
                "message": duplicate_check["error"]
            })
        
        # Create update request
        update_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "name": validated_new_table_name
                },
                "fields": "name"
            }
        }
        
        # Execute the update
        try:
            response = sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [update_request]}
            ).execute()
            
            # Extract response information
            replies = response.get("replies", [])
            if not replies:
                return compact_json_response({
                    "success": False,
                    "message": "Failed to update table title - no response from API"
                })
            
            # Check if the update was successful (the table title was actually changed)
            # Even if updateTable field is not in response, the operation might still be successful
            # We'll consider it successful if we get a reply and no error was thrown
            
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "old_table_name": validated_old_table_name,
                "new_table_name": validated_new_table_name,
                "table_id": table_id,
                "message": f"Successfully updated table '{validated_old_table_name}' title to '{validated_new_table_name}' in '{sheet_name}'"
            }
            
            # Add warning if there was a warning during duplicate check
            if "warning" in duplicate_check:
                response_data["warning"] = duplicate_check["warning"]
            
            return compact_json_response(response_data)
            
        except HttpError as error:
            error_details = error.error_details if hasattr(error, 'error_details') else str(error)
            return compact_json_response({
                "success": False,
                "message": f"Google Sheets API error: {error_details}"
            })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        })
