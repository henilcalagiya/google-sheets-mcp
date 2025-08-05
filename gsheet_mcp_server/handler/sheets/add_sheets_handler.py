from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.models import SheetInfo
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

def check_duplicate_sheet_names(sheets_service, spreadsheet_id: str, new_sheet_names: List[str]) -> Dict[str, Any]:
    """
    Check for duplicate sheet names (both within new names and against existing sheets).
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        new_sheet_names: List of new sheet names to check
    
    Returns:
        Dictionary with duplicate check results
    """
    # Check for duplicates within the new sheet names
    seen_names = set()
    duplicates_within_new = []
    
    for name in new_sheet_names:
        if name in seen_names:
            duplicates_within_new.append(name)
        else:
            seen_names.add(name)
    
    if duplicates_within_new:
        return {
            "has_duplicates": True,
            "duplicate_names": duplicates_within_new,
            "error": f"Duplicate sheet names found: {', '.join(duplicates_within_new)}"
        }
    
    # Check against existing sheets
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
        conflicts_with_existing = []
        for name in new_sheet_names:
            if name in existing_names:
                conflicts_with_existing.append(name)
        
        if conflicts_with_existing:
            return {
                "has_duplicates": True,
                "duplicate_names": conflicts_with_existing,
                "error": f"Sheet names already exist: {', '.join(conflicts_with_existing)}"
            }
        
        return {"has_duplicates": False}
        
    except Exception as e:
        # If we can't check existing sheets, proceed with warning
        return {
            "has_duplicates": False,
            "warning": f"Could not verify against existing sheets: {str(e)}"
        }

def add_sheets(sheets_service, spreadsheet_id: str, sheet_names: List[str]) -> List[SheetInfo]:
    requests = [
        {"addSheet": {"properties": {"title": name}}} for name in sheet_names
    ]
    if not requests:
        return []
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise RuntimeError(f"Error adding sheets: {error}")
    return []  # Info will be fetched after

def add_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_names: List[str]
) -> str:
    """Handler to add new sheets to a spreadsheet."""
    if not sheet_names:
        return compact_json_response({
            "success": False,
            "message": "No sheet names provided."
        })
    
    # Validate all sheet names
    validated_names = []
    invalid_names = []
    
    for name in sheet_names:
        validation = validate_sheet_name(name)
        if validation["valid"]:
            validated_names.append(validation["cleaned_name"])
        else:
            invalid_names.append({"original": name, "error": validation["error"]})
    
    if invalid_names:
        error_messages = [f"'{item['original']}': {item['error']}" for item in invalid_names]
        return compact_json_response({
            "success": False,
            "message": f"Invalid sheet names: {'; '.join(error_messages)}",
            "invalid_names": invalid_names
        })
    
    if not validated_names:
        return compact_json_response({
            "success": False,
            "message": "No valid sheet names provided after validation."
        })
    
    # Get spreadsheet ID
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    # Check for duplicate sheet names
    duplicate_check = check_duplicate_sheet_names(sheets_service, spreadsheet_id, validated_names)
    if duplicate_check["has_duplicates"]:
        return compact_json_response({
            "success": False,
            "message": duplicate_check["error"],
            "duplicate_names": duplicate_check["duplicate_names"]
        })
    
    try:
        add_sheets(sheets_service, spreadsheet_id, validated_names)
        
        response = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "added_sheets": validated_names,
            "sheets_added": len(validated_names),
            "message": f"Successfully added {len(validated_names)} sheet(s) to '{spreadsheet_name}'"
        }
        
        # Add warning if there was a warning during duplicate check
        if "warning" in duplicate_check:
            response["warning"] = duplicate_check["warning"]
        
        return compact_json_response(response)
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error adding sheets: {str(e)}"
        }) 