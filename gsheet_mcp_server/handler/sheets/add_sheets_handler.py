from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.models import SheetInfo
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response

def add_sheets(sheets_service, spreadsheet_id: str, sheet_names: List[str]) -> List[SheetInfo]:
    requests = [
        {"addSheet": {"properties": {"title": name}}} for name in sheet_names
    ]
    if not requests:
        return []
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise RuntimeError(f"Error adding sheets: {error}")
    return []  # Info will be fetched after

def add_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_names: List[str]
) -> str:
    """Handler to add new sheets to a spreadsheet."""
    if not sheet_names:
        return compact_json_response({
            "success": False,
            "message": "No sheet names provided."
        })
    
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    try:
        add_sheets(sheets_service, spreadsheet_id, sheet_names)
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "added_sheets": sheet_names,
            "sheets_added": len(sheet_names),
            "message": f"Successfully added {len(sheet_names)} sheet(s) to '{spreadsheet_name}'"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error adding sheets: {str(e)}"
        }) 