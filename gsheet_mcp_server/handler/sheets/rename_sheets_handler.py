from typing import List, Dict, Any
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

def rename_sheets(sheets_service, spreadsheet_id: str, sheet_ids: List[int], new_titles: List[str]) -> List[str]:
    requests = [
        {"updateSheetProperties": {"properties": {"sheetId": sheet_id, "title": new_title}, "fields": "title"}}
        for sheet_id, new_title in zip(sheet_ids, new_titles)
    ]
    if not requests:
        return []
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise RuntimeError(f"Error renaming sheets: {error}")
    return [f"Sheet {sheet_id} renamed to '{new_title}'" for sheet_id, new_title in zip(sheet_ids, new_titles)]

def rename_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_names: List[str],
    new_titles: List[str]
) -> str:
    """Handler to rename sheets in a Google Spreadsheet by their names."""
    
    # Validate input
    if not sheet_names:
        return compact_json_response({
            "success": False,
            "message": "No sheet names provided."
        })
    
    if len(sheet_names) != len(new_titles):
        return compact_json_response({
            "success": False,
            "message": f"Number of sheet names ({len(sheet_names)}) must match number of new titles ({len(new_titles)})."
        })
    
    # Get spreadsheet ID
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    # Get sheet IDs from sheet names
    sheet_id_map = get_sheet_ids_by_names(sheets_service, spreadsheet_id, sheet_names)
    
    # Filter out sheets that don't exist
    existing_sheet_ids = []
    existing_sheet_names = []
    existing_new_titles = []
    
    for i, sheet_name in enumerate(sheet_names):
        sheet_id = sheet_id_map.get(sheet_name)
        if sheet_id is not None:
            existing_sheet_ids.append(sheet_id)
            existing_sheet_names.append(sheet_name)
            existing_new_titles.append(new_titles[i])
        else:
            print(f"Warning: Sheet '{sheet_name}' not found, skipping.")
    
    if not existing_sheet_ids:
        return compact_json_response({
            "success": False,
            "message": "No valid sheets found to rename."
        })
    
    try:
        # Rename the sheets
        results = rename_sheets(sheets_service, spreadsheet_id, existing_sheet_ids, existing_new_titles)
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "renamed_sheets": list(zip(existing_sheet_names, existing_new_titles)),
            "sheets_renamed": len(existing_sheet_ids),
            "message": f"Successfully renamed {len(existing_sheet_ids)} sheet(s) in '{spreadsheet_name}'"
        })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error renaming sheets: {str(e)}"
        }) 