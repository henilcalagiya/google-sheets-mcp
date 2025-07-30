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
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
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


def get_table_ids_by_names(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str,
    table_names: List[str]
) -> Dict[str, Optional[str]]:
    """
    Get table IDs from spreadsheet ID, sheet name, and table names.
    Works for both single and multiple table lookups.
    
    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet containing the tables
        table_names: List of table names to find (can be single item)
    
    Returns:
        Dictionary mapping table names to their IDs (None if not found)
        
    Examples:
        # Single table lookup
        result = get_table_ids_by_names(sheets_service, "123", "Sheet1", ["SalesData"])
        # Returns: {"SalesData": "4567890123"}
        
        # Multiple table lookup
        result = get_table_ids_by_names(sheets_service, "123", "Sheet1", ["SalesData", "Inventory", "Summary"])
        # Returns: {"SalesData": "4567890123", "Inventory": "7890123456", "Summary": None}
    
    Raises:
        RuntimeError: If Google Sheets service not initialized
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        # Find the specific sheet
        for sheet in result.get("sheets", []):
            props = sheet.get("properties", {})
            if props.get("title") == sheet_name:
                tables = sheet.get("tables", [])
                
                # Create lookup dictionary for all tables in this sheet
                table_lookup = {}
                for table in tables:
                    table_name = table.get("name")
                    table_id = table.get("tableId")
                    if table_name and table_id:  # Only add if both name and ID exist
                        table_lookup[table_name] = table_id
                
                # Return results for requested table names
                results = {}
                for table_name in table_names:
                    results[table_name] = table_lookup.get(table_name)
                
                return results
        
        # Sheet not found, return None for all requested table names
        return {name: None for name in table_names}
        
    except HttpError as error:
        print(f"Error getting table IDs for spreadsheet '{spreadsheet_id}' sheet '{sheet_name}': {error}")
        return {name: None for name in table_names}
    except Exception as error:
        print(f"Unexpected error while getting table IDs: {error}")
        return {name: None for name in table_names} 