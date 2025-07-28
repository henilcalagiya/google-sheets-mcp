from typing import Optional, Dict, Any
from .api_functions import list_spreadsheets, rename_spreadsheet
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

def spreadsheet_management_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str = "",
    new_title: str = "",
    max_results: int = 10
) -> Dict[str, Any]:
    """Combined handler: List all spreadsheets and optionally rename a spreadsheet by ID."""
    rename_result = None
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if spreadsheet_id and new_title:
        rename_result = rename_spreadsheet(sheets_service, spreadsheet_id, new_title)
    spreadsheets = list_spreadsheets(drive_service, max_results)
    return {
        "spreadsheets": spreadsheets,
        "rename_result": rename_result,
        "total_spreadsheets": len(spreadsheets),
        "message": "Listed spreadsheets." if not rename_result else rename_result + ". Listed spreadsheets."
    }
