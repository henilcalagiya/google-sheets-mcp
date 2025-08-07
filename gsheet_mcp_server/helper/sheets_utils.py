"""Helper utilities for Google Sheets operations."""

from typing import Dict, Optional, List
from googleapiclient.errors import HttpError


def get_sheet_ids_by_names(
    sheets_service,
    spreadsheet_id: str,
    sheet_names: List[str]
) -> Dict[str, Optional[int]]:
    """
    Get sheet IDs from spreadsheet ID and sheet names.
    Works for both single and multiple sheet lookups.
    
    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_names: List of sheet names to find (can be single item)
    
    Returns:
        Dictionary mapping sheet names to their IDs (None if not found)
        
    Examples:
        # Single sheet lookup
        result = get_sheet_ids_by_names(sheets_service, "123", ["Sheet1"])
        # Returns: {"Sheet1": 456}
        
        # Multiple sheet lookup
        result = get_sheet_ids_by_names(sheets_service, "123", ["Sheet1", "Data", "Summary"])
        # Returns: {"Sheet1": 456, "Data": 789, "Summary": None}
    
    Raises:
        RuntimeError: If Google Sheets service not initialized
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set Google credentials environment variables.")
    
    try:
        # Get spreadsheet metadata to find sheets
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties"
        ).execute()
        
        sheets = result.get("sheets", [])
        
        # Create lookup dictionary for all sheets
        sheet_lookup = {}
        for sheet in sheets:
            props = sheet.get("properties", {})
            sheet_lookup[props.get("title")] = props.get("sheetId")
        
        # Return results for requested sheet names
        results = {}
        for sheet_name in sheet_names:
            results[sheet_name] = sheet_lookup.get(sheet_name)
        
        return results
        
    except HttpError as error:
        print(f"Error getting sheet IDs for spreadsheet '{spreadsheet_id}': {error}")
        return {name: None for name in sheet_names}
    except Exception as error:
        print(f"Unexpected error while getting sheet IDs: {error}")
        return {name: None for name in sheet_names} 