from typing import List, Dict, Any
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

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

def check_duplicate_sheet_names_for_update(sheets_service, spreadsheet_id: str, new_sheet_names: List[str], exclude_sheet_names: List[str] = None) -> Dict[str, Any]:
    """
    Check for duplicate sheet names when updating titles (excluding the sheets being updated).
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        new_sheet_names: List of new sheet names to check
        exclude_sheet_names: List of sheet names to exclude from duplicate check (the ones being updated)
    
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
    
    # Check against existing sheets (excluding the ones being updated)
    try:
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties"
        ).execute()
        
        existing_sheets = result.get("sheets", [])
        existing_names = set()
        
        for sheet in existing_sheets:
            props = sheet.get("properties", {})
            sheet_name = props.get("title", "")
            # Exclude the sheets being updated from the duplicate check
            if exclude_sheet_names and sheet_name in exclude_sheet_names:
                continue
            existing_names.add(sheet_name)
        
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
        return {
            "has_duplicates": True,
            "error": f"Error checking existing sheets: {str(e)}"
        }

def update_sheet_titles(sheets_service, spreadsheet_id: str, sheet_ids: List[int], new_titles: List[str]) -> List[str]:
    """
    Update sheet titles in a Google Spreadsheet.
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        sheet_ids: List of sheet IDs to update
        new_titles: List of new titles for the sheets
    
    Returns:
        List of updated sheet names
    """
    requests = []
    for sheet_id, new_title in zip(sheet_ids, new_titles):
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "title": new_title
                },
                "fields": "title"
            }
        })
    
    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()
    
    updated_names = []
    for reply in response.get("replies", []):
        if "updateSheetProperties" in reply:
            updated_names.append(reply["updateSheetProperties"]["properties"]["title"])
    
    return updated_names

def update_sheet_titles_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_names: List[str],
    new_titles: List[str]
) -> str:
    """
    Handler to update sheet titles in a Google Spreadsheet.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        spreadsheet_name: Name of the spreadsheet
        sheet_names: List of sheet names to update
        new_titles: List of new titles for the sheets
    
    Returns:
        JSON string with success status and updated sheets info
    """
    try:
        # Validate inputs
        if not sheet_names or not isinstance(sheet_names, list):
            return compact_json_response({
                "success": False,
                "message": "Sheet names are required and must be a list."
            })
        
        if not new_titles or not isinstance(new_titles, list):
            return compact_json_response({
                "success": False,
                "message": "New titles are required and must be a list."
            })
        
        if len(sheet_names) != len(new_titles):
            return compact_json_response({
                "success": False,
                "message": "Number of sheet names must match number of new titles."
            })
        
        if len(sheet_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one sheet name is required."
            })
        
        # Validate each new title
        valid_titles = []
        invalid_titles = []
        
        for title in new_titles:
            validation = validate_sheet_name(title)
            if validation["valid"]:
                valid_titles.append(validation["cleaned_name"])
            else:
                invalid_titles.append({"title": title, "error": validation["error"]})
        
        if invalid_titles:
            error_messages = [f"'{item['title']}': {item['error']}" for item in invalid_titles]
            return compact_json_response({
                "success": False,
                "message": f"Invalid sheet titles: {'; '.join(error_messages)}",
                "invalid_titles": invalid_titles
            })
        
        if not valid_titles:
            return compact_json_response({
                "success": False,
                "message": "No valid sheet titles provided."
            })
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })
        
        # Get sheet IDs
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, sheet_names)
        missing_sheets = [name for name in sheet_names if name not in sheet_ids]
        
        if missing_sheets:
            return compact_json_response({
                "success": False,
                "message": f"Sheets not found: {', '.join(missing_sheets)}"
            })
        
        # Check for duplicate names
        duplicate_check = check_duplicate_sheet_names_for_update(sheets_service, spreadsheet_id, valid_titles, sheet_names)
        if duplicate_check["has_duplicates"]:
            return compact_json_response({
                "success": False,
                "message": duplicate_check["error"]
            })
        
        # Update sheet titles
        try:
            sheet_id_list = [sheet_ids[name] for name in sheet_names]
            updated_names = update_sheet_titles(sheets_service, spreadsheet_id, sheet_id_list, valid_titles)
            
            # Prepare response
            renamed_sheets = list(zip(sheet_names, updated_names))
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "renamed_sheets": renamed_sheets,
                "sheets_renamed": len(updated_names),
                "message": f"Successfully updated {len(updated_names)} sheet title(s) in '{spreadsheet_name}'"
            }
            
            return compact_json_response(response_data)
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            return compact_json_response({
                "success": False,
                "message": f"Failed to update sheet titles: {error_details}",
                "error_code": e.resp.status if hasattr(e, 'resp') else None
            })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        })
