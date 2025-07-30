from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.models import SheetInfo
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

def delete_sheets(sheets_service, spreadsheet_id: str, sheet_ids: List[int]) -> List[int]:
    requests = [
        {"deleteSheet": {"sheetId": sheet_id}} for sheet_id in sheet_ids
    ]
    if not requests:
        return []
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise RuntimeError(f"Error deleting sheets: {error}")
    return sheet_ids

def delete_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_names: List[str]
) -> str:
    """Handler to delete sheets from a spreadsheet by their names."""
    
    # Validate input
    if not sheet_names:
        return compact_json_response({
            "success": False,
            "message": "No sheet names provided."
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
    
    for sheet_name in sheet_names:
        sheet_id = sheet_id_map.get(sheet_name)
        if sheet_id is not None:
            existing_sheet_ids.append(sheet_id)
            existing_sheet_names.append(sheet_name)
        else:
            print(f"Warning: Sheet '{sheet_name}' not found, skipping.")
    
    if not existing_sheet_ids:
        return compact_json_response({
            "success": False,
            "message": "No valid sheets found to delete."
        })
    
    try:
        # Delete the sheets
        deleted_ids = delete_sheets(sheets_service, spreadsheet_id, existing_sheet_ids)
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "deleted_sheet_names": existing_sheet_names,
            "sheets_deleted": len(deleted_ids),
            "message": f"Successfully deleted {len(deleted_ids)} sheet(s) from '{spreadsheet_name}'"
        })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error deleting sheets: {str(e)}"
        }) 