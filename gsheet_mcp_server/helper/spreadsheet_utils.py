"""Helper utilities for Google Sheets operations."""

from typing import Optional
from googleapiclient.errors import HttpError
from ..handler.api_functions import list_spreadsheets


def get_spreadsheet_id_by_name(
    drive_service,
    spreadsheet_name: str,
    exact_match: bool = True
) -> Optional[str]:
    """
    Convert a spreadsheet name to its ID using the existing list_spreadsheets function.
    
    Args:
        drive_service: Google Drive API service instance
        spreadsheet_name: Name of the spreadsheet to find
        exact_match: If True, looks for exact name match. If False, looks for partial matches.
    
    Returns:
        Spreadsheet ID if found, None otherwise
    
    Raises:
        RuntimeError: If Google Drive service is not initialized
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        # Use the existing list_spreadsheets function
        spreadsheets = list_spreadsheets(drive_service, max_results=100)
        
        # Search through the results
        for spreadsheet in spreadsheets:
            current_name = spreadsheet["name"]
            
            if exact_match:
                if current_name == spreadsheet_name:
                    return spreadsheet["spreadsheet_id"]
            else:
                if spreadsheet_name.lower() in current_name.lower():
                    return spreadsheet["spreadsheet_id"]
        
        # No match found
        return None
        
    except Exception as error:
        print(f"Unexpected error while searching for spreadsheet '{spreadsheet_name}': {error}")
        return None 