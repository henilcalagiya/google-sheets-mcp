"""Handler for deleting tables from Google Sheets."""

from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

def delete_table_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_names: List[str]
) -> str:
    """
    Delete tables from Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the tables
        table_names: List of table names to delete
    
    Returns:
        str: Success message with deletion details
    """
    try:
        # Validate inputs
        if not table_names or len(table_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one table name is required."
            })
        
        # Validate table names
        validated_table_names = []
        invalid_table_names = []
        
        for table_name in table_names:
            if not table_name or table_name.strip() == "":
                invalid_table_names.append({"name": table_name, "error": "Table name cannot be empty"})
                continue
            
            validated_name = table_name.strip()
            validated_table_names.append(validated_name)
        
        if invalid_table_names:
            error_messages = [f"'{item['name']}': {item['error']}" for item in invalid_table_names]
            return compact_json_response({
                "success": False,
                "message": f"Invalid table names: {'; '.join(error_messages)}",
                "invalid_table_names": invalid_table_names
            })
        
        if not validated_table_names:
            return compact_json_response({
                "success": False,
                "message": "No valid table names provided after validation."
            })
        
        # Check for duplicate table names in the list
        seen_names = set()
        duplicate_names = []
        for table_name in validated_table_names:
            if table_name in seen_names:
                duplicate_names.append(table_name)
            else:
                seen_names.add(table_name)
        
        if duplicate_names:
            return compact_json_response({
                "success": False,
                "message": f"Duplicate table names in list: {', '.join(duplicate_names)}"
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
        
        # Get table IDs
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, validated_table_names)
        
        # Filter out tables that don't exist
        existing_table_ids = []
        existing_table_names = []
        non_existent_tables = []
        
        for table_name in validated_table_names:
            table_id = table_ids.get(table_name)
            if table_id is not None:
                existing_table_ids.append(table_id)
                existing_table_names.append(table_name)
            else:
                non_existent_tables.append(table_name)
        
        if not existing_table_ids:
            return compact_json_response({
                "success": False,
                "message": "No valid tables found to delete."
            })
        
        # Create delete requests
        delete_requests = []
        for table_id in existing_table_ids:
            delete_requests.append({
                "deleteTable": {
                    "tableId": table_id
                }
            })
        
        # Execute batch delete
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": delete_requests}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        deleted_count = len(replies)
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "deleted_table_names": existing_table_names,
            "tables_deleted": deleted_count,
            "message": f"Successfully deleted {deleted_count} table(s) from '{sheet_name}'"
        }
        
        # Add information about non-existent tables
        if non_existent_tables:
            response_data["non_existent_tables"] = non_existent_tables
            response_data["message"] += f" (Skipped {len(non_existent_tables)} non-existent table(s))"
        
        return compact_json_response(response_data)
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error deleting tables: {str(e)}"
        }) 