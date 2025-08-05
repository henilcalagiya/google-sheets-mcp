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

def check_duplicate_sheet_names_for_rename(sheets_service, spreadsheet_id: str, new_sheet_names: List[str], exclude_sheet_names: List[str] = None) -> Dict[str, Any]:
    """
    Check for duplicate sheet names when renaming (excluding the sheets being renamed).
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        new_sheet_names: List of new sheet names to check
        exclude_sheet_names: List of sheet names to exclude from duplicate check (the ones being renamed)
    
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
    
    # Check against existing sheets (excluding the ones being renamed)
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
            # Exclude the sheets being renamed from the duplicate check
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
        # If we can't check existing sheets, proceed with warning
        return {
            "has_duplicates": False,
            "warning": f"Could not verify against existing sheets: {str(e)}"
        }

def rename_sheets(sheets_service, spreadsheet_id: str, sheet_ids: List[int], new_titles: List[str]) -> List[str]:
    """
    Rename sheets using Google Sheets API batchUpdate.
    
    Args:
        sheets_service: Google Sheets service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_ids: List of sheet IDs to rename
        new_titles: List of new titles for the sheets
    
    Returns:
        List of success messages for each renamed sheet
    
    Raises:
        RuntimeError: If the API call fails
    """
    requests = [
        {"updateSheetProperties": {"properties": {"sheetId": sheet_id, "title": new_title}, "fields": "title"}}
        for sheet_id, new_title in zip(sheet_ids, new_titles)
    ]
    
    if not requests:
        return []
    
    try:
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        
        # Verify the response
        replies = response.get("replies", [])
        if len(replies) != len(requests):
            raise RuntimeError(f"Expected {len(requests)} replies, got {len(replies)}")
        
        return [f"Sheet {sheet_id} renamed to '{new_title}'" for sheet_id, new_title in zip(sheet_ids, new_titles)]
        
    except HttpError as error:
        error_details = error.error_details if hasattr(error, 'error_details') else str(error)
        raise RuntimeError(f"Google Sheets API error: {error_details}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error renaming sheets: {str(e)}")

def rename_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_names: List[str],
    new_titles: List[str]
) -> str:
    """
    Handler to rename sheets in a Google Spreadsheet by their names.
    
    This function validates inputs, checks for duplicates, and performs the rename operation
    using the Google Sheets API updateSheetProperties request.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_names: List of sheet names to rename
        new_titles: List of new titles for the sheets (must match sheet_names count)
    
    Returns:
        JSON string with success status and rename details
    """
    
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
    
    # Validate all new sheet names
    validated_new_titles = []
    invalid_names = []
    
    for name in new_titles:
        validation = validate_sheet_name(name)
        if validation["valid"]:
            validated_new_titles.append(validation["cleaned_name"])
        else:
            invalid_names.append({"original": name, "error": validation["error"]})
    
    if invalid_names:
        error_messages = [f"'{item['original']}': {item['error']}" for item in invalid_names]
        return compact_json_response({
            "success": False,
            "message": f"Invalid new sheet names: {'; '.join(error_messages)}",
            "invalid_names": invalid_names
        })
    
    if not validated_new_titles:
        return compact_json_response({
            "success": False,
            "message": "No valid new sheet names provided after validation."
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
            existing_new_titles.append(validated_new_titles[i])
        else:
            print(f"Warning: Sheet '{sheet_name}' not found, skipping.")
    
    if not existing_sheet_ids:
        return compact_json_response({
            "success": False,
            "message": "No valid sheets found to rename."
        })
    
    # Check for duplicate sheet names (excluding the sheets being renamed)
    duplicate_check = check_duplicate_sheet_names_for_rename(
        sheets_service, 
        spreadsheet_id, 
        existing_new_titles, 
        exclude_sheet_names=existing_sheet_names
    )
    if duplicate_check["has_duplicates"]:
        return compact_json_response({
            "success": False,
            "message": duplicate_check["error"],
            "duplicate_names": duplicate_check["duplicate_names"]
        })
    
    try:
        # Rename the sheets
        results = rename_sheets(sheets_service, spreadsheet_id, existing_sheet_ids, existing_new_titles)
        
        response = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "renamed_sheets": list(zip(existing_sheet_names, existing_new_titles)),
            "sheets_renamed": len(existing_sheet_ids),
            "message": f"Successfully renamed {len(existing_sheet_ids)} sheet(s) in '{spreadsheet_name}'"
        }
        
        # Add warning if there was a warning during duplicate check
        if "warning" in duplicate_check:
            response["warning"] = duplicate_check["warning"]
        
        return compact_json_response(response)
        
    except RuntimeError as e:
        return compact_json_response({
            "success": False,
            "message": f"Error renaming sheets: {str(e)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }) 