from typing import List, Dict, Any
from .api_functions import rename_sheets

def rename_sheets_handler(
    sheets_service,
    spreadsheet_id: str,
    sheet_ids: List[int],
    new_titles: List[str]
) -> Dict[str, Any]:
    """Handler to rename sheets in a Google Spreadsheet."""
    results = rename_sheets(sheets_service, spreadsheet_id, sheet_ids, new_titles)
    return {
        "renamed": results,
        "message": f"Renamed {len(results)} sheet(s)." if results else "No sheets renamed."
    } 