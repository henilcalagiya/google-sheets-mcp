from typing import Optional, Dict, Any
from .api_functions import list_spreadsheets, rename_spreadsheet

def spreadsheet_management_handler(
    drive_service,
    sheets_service,
    spreadsheet_id: str = "",
    new_title: str = "",
    max_results: int = 10
) -> Dict[str, Any]:
    """Combined handler: List all spreadsheets and optionally rename a spreadsheet by ID."""
    rename_result = None
    if spreadsheet_id.strip() and new_title.strip():
        rename_result = rename_spreadsheet(sheets_service, spreadsheet_id, new_title)
    spreadsheets = list_spreadsheets(drive_service, max_results)
    return {
        "spreadsheets": spreadsheets,
        "rename_result": rename_result,
        "message": "Listed spreadsheets." if not rename_result else rename_result + ". Listed spreadsheets."
    }
