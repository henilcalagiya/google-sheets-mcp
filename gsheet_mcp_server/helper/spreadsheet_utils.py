"""Helper utilities for Google Sheets operations."""

from typing import Optional
from googleapiclient.errors import HttpError


def get_spreadsheet_id_by_name(
    drive_service,
    spreadsheet_name: str,
    exact_match: bool = True
) -> Optional[str]:
    """
    Convert a spreadsheet name to its ID by making direct API call to Google Drive.
    
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
        # Make direct API call to Google Drive
        results = (
            drive_service.files()
            .list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=100,
                fields="files(id,name)",
            )
            .execute()
        )
        files = results.get("files", [])
        
        # Search through the results
        for file in files:
            current_name = file["name"]
            
            if exact_match:
                if current_name == spreadsheet_name:
                    return file["id"]
            else:
                if spreadsheet_name.lower() in current_name.lower():
                    return file["id"]
        
        # No match found
        return None
        
    except HttpError as error:
        print(f"Error searching for spreadsheet '{spreadsheet_name}': {error}")
        return None
    except Exception as error:
        print(f"Unexpected error while searching for spreadsheet '{spreadsheet_name}': {error}")
        return None 