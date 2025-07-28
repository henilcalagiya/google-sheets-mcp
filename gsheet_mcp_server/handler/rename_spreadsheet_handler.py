from typing import Dict, Any
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

def rename_spreadsheet(sheets_service, spreadsheet_id: str, new_title: str) -> str:
    """Rename a spreadsheet by its ID."""
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
        return f"Spreadsheet {spreadsheet_id} renamed to '{new_title}'"
    except HttpError as error:
        raise RuntimeError(f"Error renaming spreadsheet: {error}")

def rename_spreadsheet_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    new_title: str
) -> Dict[str, Any]:
    """Handler to rename a spreadsheet by name."""
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return {
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        }
    
    try:
        rename_spreadsheet(sheets_service, spreadsheet_id, new_title)
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "new_title": new_title,
            "message": f"Successfully renamed spreadsheet '{spreadsheet_name}' to '{new_title}'"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error renaming spreadsheet: {str(e)}"
        } 