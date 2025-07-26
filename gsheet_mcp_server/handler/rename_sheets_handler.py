from typing import List, Dict, Any
from .api_functions import rename_sheets
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

def rename_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_ids: List[int],
    new_titles: List[str]
) -> Dict[str, Any]:
    """Handler to rename sheets in a Google Spreadsheet."""
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    results = rename_sheets(sheets_service, spreadsheet_id, sheet_ids, new_titles)
    return {
        "renamed": results,
        "message": f"Renamed {len(results)} sheet(s)." if results else "No sheets renamed."
    } 