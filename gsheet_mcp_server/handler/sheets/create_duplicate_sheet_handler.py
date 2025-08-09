from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response
import re

def validate_sheet_name(name: str) -> Dict[str, Any]:
    """
    Validate a sheet name according to Google Sheets rules.
    
    Args:
        name: Sheet name to validate
    
    Returns:
        Dictionary with validation result
    """
    if not name or name.strip() == "":
        return {"valid": False, "error": "Sheet name cannot be empty"}
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Check length (Google Sheets limit is 100 characters)
    if len(name) > 100:
        return {"valid": False, "error": f"Sheet name '{name}' is too long (max 100 characters)"}
    
    # Check for invalid characters
    # Google Sheets doesn't allow: [ ] * ? / \
    invalid_chars = ['[', ']', '*', '?', '/', '\\']
    for char in invalid_chars:
        if char in name:
            return {"valid": False, "error": f"Sheet name '{name}' contains invalid character '{char}'"}
    
    # Check for reserved names (Google Sheets has some reserved names)
    reserved_names = ['Sheet1', 'Sheet2', 'Sheet3']  # Common default names
    if name in reserved_names:
        return {"valid": False, "error": f"Sheet name '{name}' is a reserved name"}
    
    return {"valid": True, "cleaned_name": name}

def check_duplicate_sheet_name_for_duplicate(sheets_service, spreadsheet_id: str, new_sheet_name: str) -> Dict[str, Any]:
    """
    Check for duplicate sheet names when creating duplicate (excluding the source sheet).
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        new_sheet_name: New sheet name to check
    
    Returns:
        Dictionary with duplicate check results
    """
    try:
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties"
        ).execute()
        
        existing_sheets = result.get("sheets", [])
        existing_names = set()
        
        for sheet in existing_sheets:
            props = sheet.get("properties", {})
            existing_names.add(props.get("title", ""))
        
        # Check for conflicts with existing sheets
        if new_sheet_name in existing_names:
            return {
                "has_duplicates": True,
                "duplicate_names": [new_sheet_name],
                "error": f"Sheet name '{new_sheet_name}' already exists"
            }
        
        return {"has_duplicates": False}
        
    except Exception as e:
        # If we can't check existing sheets, proceed with warning
        return {
            "has_duplicates": False,
            "warning": f"Could not verify against existing sheets: {str(e)}"
        }

def create_duplicate_sheet(sheets_service, spreadsheet_id: str, source_sheet_id: int, new_sheet_name: str = None, insert_position: int = None) -> Dict[str, Any]:
    """Create a duplicate sheet within the same spreadsheet."""
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
        
        # Extract the created sheet information
        reply = response.get("replies", [{}])[0]
        if "duplicateSheet" in reply:
            sheet_props = reply["duplicateSheet"]["properties"]
            return {
                "success": True,
                "sheet_id": sheet_props["sheetId"],
                "title": sheet_props["title"],
                "index": sheet_props["index"]
            }
        else:
            return {
                "success": False,
                "error": "Failed to create duplicate sheet"
            }
            
    except HttpError as e:
        return {
            "success": False,
            "error": f"Failed to create duplicate sheet: {str(e)}"
        }

def create_duplicate_sheet_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    source_sheet_name: str,
    new_sheet_name: str = None,
    insert_position: int = None
) -> str:
    """
    Handler to create a duplicate of an existing sheet.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        spreadsheet_name: Name of the spreadsheet
        source_sheet_name: Name of the sheet to duplicate
        new_sheet_name: Name for the duplicated sheet (optional)
        insert_position: Position to insert the duplicated sheet (optional)
    
    Returns:
        JSON string with success status and duplicate sheet info
    """
    try:
        # Validate inputs
        if not source_sheet_name or not isinstance(source_sheet_name, str):
            return compact_json_response({
                "success": False,
                "message": "Source sheet name is required and must be a string."
            })
        
        # Validate new sheet name if provided
        if new_sheet_name:
            validation = validate_sheet_name(new_sheet_name)
            if not validation["valid"]:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid new sheet name: {validation['error']}"
                })
            new_sheet_name = validation["cleaned_name"]
        
        # Validate insert position if provided
        if insert_position is not None:
            if not isinstance(insert_position, int) or insert_position < 0:
                return compact_json_response({
                    "success": False,
                    "message": "Insert position must be a non-negative integer."
                })
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })
        
        # Get source sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [source_sheet_name])
        source_sheet_id = sheet_ids.get(source_sheet_name)
        if source_sheet_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Source sheet '{source_sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
            })
        
        # Check for duplicate name if new name is provided
        if new_sheet_name:
            duplicate_check = check_duplicate_sheet_name_for_duplicate(sheets_service, spreadsheet_id, new_sheet_name)
            if duplicate_check["has_duplicates"]:
                return compact_json_response({
                    "success": False,
                    "message": duplicate_check["error"]
                })
        
        # Create duplicate sheet
        try:
            result = create_duplicate_sheet(sheets_service, spreadsheet_id, source_sheet_id, new_sheet_name, insert_position)
            
            if result["success"]:
                # Prepare response
                response_data = {
                    "success": True,
                    "spreadsheet_name": spreadsheet_name,
                    "source_sheet_name": source_sheet_name,
                    "new_sheet_name": result["title"],
                    "new_sheet_index": result["index"],
                    "insert_position": insert_position,
                    "message": f"Successfully created duplicate of sheet '{source_sheet_name}' as '{result['title']}' in '{spreadsheet_name}'",
                    "sheet_details": {
                        "sheet_id": result["sheet_id"],
                        "title": result["title"],
                        "index": result["index"]
                    }
                }
                
                return compact_json_response(response_data)
            else:
                return compact_json_response({
                    "success": False,
                    "message": result["error"]
                })
                
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            return compact_json_response({
                "success": False,
                "message": f"Failed to create duplicate sheet: {error_details}",
                "error_code": e.resp.status if hasattr(e, 'resp') else None
            })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        })
