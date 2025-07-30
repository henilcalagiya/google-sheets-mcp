from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

def duplicate_sheet(sheets_service, spreadsheet_id: str, source_sheet_id: int, new_sheet_name: str = None, insert_position: int = None) -> Dict[str, Any]:
    """Duplicate a sheet within the same spreadsheet."""
    try:
        # Prepare the duplicate sheet request
        request = {
            "duplicateSheet": {
                "sourceSheetId": source_sheet_id,
                "insertSheetIndex": insert_position,  # Will be inserted at specified position or at the end if None
                "newSheetId": None,  # Let Google assign a new ID
                "newSheetName": new_sheet_name
            }
        }
        
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [request]}
        ).execute()
        
        # Extract the new sheet info from response
        replies = response.get("replies", [])
        if replies and "duplicateSheet" in replies[0]:
            new_sheet = replies[0]["duplicateSheet"]["properties"]
            return {
                "new_sheet_id": new_sheet["sheetId"],
                "new_sheet_name": new_sheet["title"],
                "new_sheet_index": new_sheet["index"]
            }
        else:
            raise RuntimeError("Failed to duplicate sheet - no response data")
            
    except HttpError as error:
        raise RuntimeError(f"Error duplicating sheet: {error}")

def duplicate_sheet_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    source_sheet_name: str,
    new_sheet_name: str = None,
    insert_position: int = None
) -> str:
    """Handler to duplicate a sheet by name."""
    
    # Validate input
    if not source_sheet_name:
        return compact_json_response({
            "success": False,
            "message": "Source sheet name is required."
        })
    
    # Get spreadsheet ID
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    # Get source sheet ID
    sheet_id_map = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [source_sheet_name])
    source_sheet_id = sheet_id_map.get(source_sheet_name)
    
    if source_sheet_id is None:
        return compact_json_response({
            "success": False,
            "message": f"Source sheet '{source_sheet_name}' not found in '{spreadsheet_name}'."
        })
    
    # Generate new sheet name if not provided
    if not new_sheet_name:
        new_sheet_name = f"{source_sheet_name} (Copy)"
    
    try:
        # Duplicate the sheet
        result = duplicate_sheet(sheets_service, spreadsheet_id, source_sheet_id, new_sheet_name, insert_position)
        
        position_info = f" at position {insert_position}" if insert_position is not None else " at the end"
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "source_sheet_name": source_sheet_name,
            "new_sheet_name": result["new_sheet_name"],
            "new_sheet_id": result["new_sheet_id"],
            "new_sheet_index": result["new_sheet_index"],
            "insert_position": insert_position,
            "message": f"Successfully duplicated sheet '{source_sheet_name}' to '{new_sheet_name}'{position_info} in '{spreadsheet_name}'"
        })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error duplicating sheet: {str(e)}"
        }) 