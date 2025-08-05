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
    Check for duplicate sheet names when duplicating (excluding the source sheet).
    
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
    
    # Validate new sheet name
    validation = validate_sheet_name(new_sheet_name)
    if not validation["valid"]:
        return compact_json_response({
            "success": False,
            "message": f"Invalid new sheet name: {validation['error']}"
        })
    
    validated_new_sheet_name = validation["cleaned_name"]
    
    # Check for duplicate sheet names
    duplicate_check = check_duplicate_sheet_name_for_duplicate(sheets_service, spreadsheet_id, validated_new_sheet_name)
    if duplicate_check["has_duplicates"]:
        return compact_json_response({
            "success": False,
            "message": duplicate_check["error"],
            "duplicate_names": duplicate_check["duplicate_names"]
        })
    
    try:
        # Duplicate the sheet
        result = duplicate_sheet(sheets_service, spreadsheet_id, source_sheet_id, validated_new_sheet_name, insert_position)
        
        position_info = f" at position {insert_position}" if insert_position is not None else " at the end"
        
        response = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "source_sheet_name": source_sheet_name,
            "new_sheet_name": result["new_sheet_name"],
            "new_sheet_index": result["new_sheet_index"],
            "insert_position": insert_position,
            "message": f"Successfully duplicated sheet '{source_sheet_name}' to '{validated_new_sheet_name}'{position_info} in '{spreadsheet_name}'"
        }
        
        # Add warning if there was a warning during duplicate check
        if "warning" in duplicate_check:
            response["warning"] = duplicate_check["warning"]
        
        return compact_json_response(response)
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error duplicating sheet: {str(e)}"
        }) 