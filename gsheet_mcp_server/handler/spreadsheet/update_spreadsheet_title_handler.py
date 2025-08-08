from typing import Dict, Any
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_spreadsheet_title(sheets_service, spreadsheet_id: str, new_title: str) -> str:
    """Update a spreadsheet title by its ID."""
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "updateSpreadsheetProperties": {
                            "properties": {"title": new_title},
                            "fields": "title"
                        }
                    }
                ]
            }
        ).execute()
        return f"Spreadsheet {spreadsheet_id} title updated to '{new_title}'"
    except HttpError as error:
        raise RuntimeError(f"Error updating spreadsheet title: {error}")

def update_spreadsheet_title_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    new_title: str
) -> str:
    """Handler to update a spreadsheet title by name."""
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    try:
        update_spreadsheet_title(sheets_service, spreadsheet_id, new_title)
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "new_title": new_title,
            "message": f"Successfully updated spreadsheet '{spreadsheet_name}' title to '{new_title}'"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error updating spreadsheet title: {str(e)}"
        })
