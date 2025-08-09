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
        
    except HttpError as e:
        return {
            "has_duplicates": True,
            "error": f"Error checking existing sheets: {str(e)}"
        }

def create_sheets(sheets_service, spreadsheet_id: str, sheet_names: List[str]) -> List[SheetInfo]:
    """
    Create new sheets in a Google Spreadsheet.
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        sheet_names: List of sheet names to create
    
    Returns:
        List of created sheet information
    """
    requests = []
    for sheet_name in sheet_names:
        requests.append({
            "addSheet": {
                "properties": {
                    "title": sheet_name
                }
            }
        })
    
    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()
    
    created_sheets = []
    for reply in response.get("replies", []):
        if "addSheet" in reply:
            sheet_props = reply["addSheet"]["properties"]
            created_sheets.append(SheetInfo(
                sheet_id=sheet_props["sheetId"],
                title=sheet_props["title"],
                index=sheet_props["index"],
                grid_properties=sheet_props.get("gridProperties", {"rowCount": 1000, "columnCount": 26})
            ))
    
    return created_sheets

def create_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_names: List[str]
) -> str:
    """
    Handler to create new sheets in a Google Spreadsheet.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        spreadsheet_name: Name of the spreadsheet
        sheet_names: List of sheet names to create
    
    Returns:
        JSON string with success status and created sheets info
    """
    try:
        # Validate inputs
        if not sheet_names or not isinstance(sheet_names, list):
            return compact_json_response({
                "success": False,
                "message": "Sheet names are required and must be a list."
            })
        
        if len(sheet_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one sheet name is required."
            })
        
        # Validate each sheet name
        valid_names = []
        invalid_names = []
        
        for name in sheet_names:
            validation = validate_sheet_name(name)
            if validation["valid"]:
                valid_names.append(validation["cleaned_name"])
            else:
                invalid_names.append({"name": name, "error": validation["error"]})
        
        if invalid_names:
            error_messages = [f"'{item['name']}': {item['error']}" for item in invalid_names]
            return compact_json_response({
                "success": False,
                "message": f"Invalid sheet names: {'; '.join(error_messages)}",
                "invalid_names": invalid_names
            })
        
        if not valid_names:
            return compact_json_response({
                "success": False,
                "message": "No valid sheet names provided."
            })
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })
        
        # Check for duplicate names
        duplicate_check = check_duplicate_sheet_names(sheets_service, spreadsheet_id, valid_names)
        if duplicate_check["has_duplicates"]:
            return compact_json_response({
                "success": False,
                "message": duplicate_check["error"]
            })
        
        # Create sheets
        try:
            created_sheets = create_sheets(sheets_service, spreadsheet_id, valid_names)
            
            # Prepare response
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "created_sheets": valid_names,
                "sheets_created": len(created_sheets),
                "message": f"Successfully created {len(created_sheets)} sheet(s) in '{spreadsheet_name}'",
                "sheet_details": [
                    {
                        "sheet_id": sheet.sheet_id,
                        "title": sheet.title,
                        "index": sheet.index
                    }
                    for sheet in created_sheets
                ]
            }
            
            return compact_json_response(response_data)
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            return compact_json_response({
                "success": False,
                "message": f"Failed to create sheets: {error_details}",
                "error_code": e.resp.status if hasattr(e, 'resp') else None
            })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        })
