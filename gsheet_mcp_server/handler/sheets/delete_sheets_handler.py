from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.models import SheetInfo
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
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

def check_last_sheet_deletion(sheets_service, spreadsheet_id: str, sheets_to_delete: List[str]) -> Dict[str, Any]:
    """
    Check if deleting the specified sheets would leave the spreadsheet with no sheets.
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        sheets_to_delete: List of sheet names to be deleted
    
    Returns:
        Dictionary with safety check results
    """
    try:
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties"
        ).execute()
        
        all_sheets = result.get("sheets", [])
        total_sheets = len(all_sheets)
        sheets_to_delete_set = set(sheets_to_delete)
        
        # Count how many sheets would remain after deletion
        remaining_sheets = 0
        for sheet in all_sheets:
            props = sheet.get("properties", {})
            sheet_name = props.get("title", "")
            if sheet_name not in sheets_to_delete_set:
                remaining_sheets += 1
        
        if remaining_sheets == 0:
            return {
                "would_delete_all": True,
                "total_sheets": total_sheets,
                "sheets_to_delete": len(sheets_to_delete),
                "error": f"Cannot delete all sheets. Spreadsheet must have at least one sheet."
            }
        
        return {
            "would_delete_all": False,
            "total_sheets": total_sheets,
            "remaining_sheets": remaining_sheets,
            "sheets_to_delete": len(sheets_to_delete)
        }
        
    except Exception as e:
        # If we can't check, proceed with warning
        return {
            "would_delete_all": False,
            "warning": f"Could not verify sheet count: {str(e)}"
        }

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
    
    # Check if deleting would leave no sheets
    safety_check = check_last_sheet_deletion(sheets_service, spreadsheet_id, sheet_names)
    if safety_check["would_delete_all"]:
        return compact_json_response({
            "success": False,
            "message": safety_check["error"],
            "total_sheets": safety_check["total_sheets"],
            "sheets_to_delete": safety_check["sheets_to_delete"]
        })
    
    # Get sheet IDs from sheet names
    sheet_id_map = get_sheet_ids_by_names(sheets_service, spreadsheet_id, sheet_names)
    
    # Filter out sheets that don't exist
    existing_sheet_ids = []
    existing_sheet_names = []
    non_existent_sheets = []
    
    for sheet_name in sheet_names:
        sheet_id = sheet_id_map.get(sheet_name)
        if sheet_id is not None:
            existing_sheet_ids.append(sheet_id)
            existing_sheet_names.append(sheet_name)
        else:
            non_existent_sheets.append(sheet_name)
    
    if not existing_sheet_ids:
        return compact_json_response({
            "success": False,
            "message": "No valid sheets found to delete."
        })
    
    try:
        # Delete the sheets
        deleted_ids = delete_sheets(sheets_service, spreadsheet_id, existing_sheet_ids)
        
        response = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "deleted_sheet_names": existing_sheet_names,
            "sheets_deleted": len(deleted_ids),
            "message": f"Successfully deleted {len(deleted_ids)} sheet(s) from '{spreadsheet_name}'"
        }
        
        # Add information about non-existent sheets
        if non_existent_sheets:
            response["non_existent_sheets"] = non_existent_sheets
            response["message"] += f" (Skipped {len(non_existent_sheets)} non-existent sheet(s))"
        
        # Add safety check information
        if "remaining_sheets" in safety_check:
            response["remaining_sheets"] = safety_check["remaining_sheets"]
        
        # Add warning if there was a warning during safety check
        if "warning" in safety_check:
            response["warning"] = safety_check["warning"]
        
        return compact_json_response(response)
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error deleting sheets: {str(e)}"
        }) 