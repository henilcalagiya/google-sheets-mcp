from typing import List, Dict, Any, Optional
from .api_functions import add_sheets, delete_sheets, rename_sheets, list_sheets
from gsheet_mcp_server.models import SheetInfo

def sheets_management_handler(
    sheets_service,
    spreadsheet_id: str,
    add_sheet_names: Optional[List[str]] = None,
    delete_sheet_ids: Optional[List[int]] = None,
    rename_sheets_map: Optional[Dict[int, str]] = None
) -> Dict[str, Any]:
    added_sheets = []
    deleted_ids = []
    renamed_sheets = []
    if add_sheet_names:
        add_sheets(sheets_service, spreadsheet_id, add_sheet_names)
    if delete_sheet_ids:
        delete_sheets(sheets_service, spreadsheet_id, delete_sheet_ids)
        deleted_ids = delete_sheet_ids
    if rename_sheets_map:
        renamed_sheets = rename_sheets(sheets_service, spreadsheet_id, rename_sheets_map)
    # Always list all sheets after any operation
    sheet_infos = list_sheets(sheets_service, spreadsheet_id)
    # If sheets were added, get their info
    if add_sheet_names:
        for info in sheet_infos:
            if info.title in add_sheet_names:
                added_sheets.append(info)
    msg = []
    if added_sheets:
        msg.append(f"Added {len(added_sheets)} sheet(s)")
    if deleted_ids:
        msg.append(f"Deleted {len(deleted_ids)} sheet(s)")
    if renamed_sheets:
        msg.append(f"Renamed {len(renamed_sheets)} sheet(s)")
    if not msg:
        msg.append("Listed sheets.")
    return {
        "sheets": [s.dict() for s in sheet_infos],
        "added": [s.dict() for s in added_sheets],
        "deleted": deleted_ids,
        "renamed": renamed_sheets,
        "message": ", ".join(msg)
    } 