"""Handler for deleting tables from Google Sheets."""

from typing import List, Any, Dict
from googleapiclient.errors import HttpError
import re
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
    Delete one or more tables from a Google Spreadsheet.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the tables
        table_names: List of table names to delete
    
    Returns:
        str: Success message with table details
    """
    try:
        # Validate inputs
        if not table_names or len(table_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one table name is required."
            })
        
        # Validate each table name
        for table_name in table_names:
            if not table_name or table_name.strip() == "":
                return compact_json_response({
                    "success": False,
                    "message": "All table names must be non-empty."
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
        # Collect all delete requests
        delete_requests = []
        deleted_tables = []
        failed_tables = []
        
        for table_name in table_names:
            # Get table ID using the table name
            table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [table_name])
            table_id = table_ids.get(table_name)
            if not table_id:
                failed_tables.append(table_name)
                continue
            
            # Create delete table request
            delete_request = {
                "deleteTable": {
                    "tableId": table_id
                }
            }
            delete_requests.append(delete_request)
            deleted_tables.append(table_name)
        
        # If no tables could be deleted, return error
        if len(deleted_tables) == 0:
            failed_list = ", ".join(failed_tables)
            return compact_json_response({
                "success": False,
                "message": f"No tables could be deleted. Failed tables: {failed_list}"
            })
        
        # Prepare batch update request
        batch_request = {
            "requests": delete_requests
        }
        
        # Execute batch update
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_request
        ).execute()
        
        # Prepare success message
        success_message = f"Successfully deleted {len(deleted_tables)} table(s) from sheet '{sheet_name}' in spreadsheet '{spreadsheet_name}': {', '.join(deleted_tables)}"
        
        # Add information about failed tables if any
        if failed_tables:
            failed_list = ", ".join(failed_tables)
            success_message += f"\nFailed to delete: {failed_list}"
        
        return compact_json_response({
            "success": True,
            "message": success_message,
            "data": {
                "deleted_tables": deleted_tables,
                "failed_tables": failed_tables,
                "sheet_name": sheet_name,
                "spreadsheet_name": spreadsheet_name
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error deleting tables: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        })

