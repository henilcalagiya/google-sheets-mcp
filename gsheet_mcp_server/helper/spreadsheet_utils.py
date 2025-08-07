"""Helper utilities for Google Sheets operations."""

from typing import Optional, List, Dict, Any
from googleapiclient.errors import HttpError


def get_spreadsheet_id_by_name(
    drive_service,
    spreadsheet_name: str
) -> Optional[str]:
    """
    Convert a spreadsheet name to its ID by making direct API call to Google Drive.
    
    Args:
        drive_service: Google Drive API service instance
        spreadsheet_name: Name of the spreadsheet to find
    
    Returns:
        Spreadsheet ID if exactly one match found, None otherwise
    
    Raises:
        RuntimeError: If Google Drive service not initialized or if multiple files with same name found
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set Google credentials environment variables.")
    
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
        
        # Collect all files with exact name match
        matching_files = []
        for file in files:
            current_name = file["name"]
            if current_name == spreadsheet_name:
                matching_files.append({
                    "id": file["id"],
                    "name": file["name"]
                })
        
        # Check for errors based on number of matches
        if len(matching_files) == 0:
            raise RuntimeError(f"No spreadsheet found with name '{spreadsheet_name}'")
        elif len(matching_files) > 1:
            file_ids = [file["id"] for file in matching_files]
            raise RuntimeError(f"Multiple spreadsheets found with name '{spreadsheet_name}'. IDs: {file_ids}")
        
        # Return the single matching file's ID
        return matching_files[0]["id"]
        
    except HttpError as error:
        print(f"Error searching for spreadsheet '{spreadsheet_name}': {error}")
        return None
    except Exception as error:
        print(f"Unexpected error while searching for spreadsheet '{spreadsheet_name}': {error}")
        return None





 


 