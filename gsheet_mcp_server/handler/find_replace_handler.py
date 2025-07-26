from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

class FindReplaceRequest(BaseModel):
    """Request model for find and replace operation."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    search_range: str = Field(..., description="Range to search in (e.g., 'Sheet1!A1:Z100')")
    find_text: str = Field(..., description="Text to find")
    replace_text: str = Field(..., description="Text to replace with")

class FindReplaceResponse(BaseModel):
    """Response model for find and replace operation."""
    spreadsheet_id: str
    search_range: str
    find_text: str
    replace_text: str
    updated_cells: int
    message: str

def find_replace_text(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    search_range: str,
    find_text: str,
    replace_text: str
) -> Dict[str, Any]:
    """
    Find and replace text in a specific range in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        search_range: Range to search in (e.g., 'Sheet1!A1:Z100')
        find_text: Text to find
        replace_text: Text to replace with
    
    Returns:
        Dict containing find and replace operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        # First, read the data from the range
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=search_range
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return {
                "spreadsheet_id": spreadsheet_id,
                "search_range": search_range,
                "find_text": find_text,
                "replace_text": replace_text,
                "updated_cells": 0,
                "message": f"No data found in range {search_range}"
            }
        
        # Perform find and replace on the data
        updated_values = []
        updated_cells = 0
        
        for row in values:
            updated_row = []
            for cell_value in row:
                if isinstance(cell_value, str) and find_text in cell_value:
                    updated_cell = cell_value.replace(find_text, replace_text)
                    updated_cells += 1
                else:
                    updated_cell = cell_value
                updated_row.append(updated_cell)
            updated_values.append(updated_row)
        
        # Write the updated data back to the range
        if updated_cells > 0:
            update_result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=search_range,
                valueInputOption='USER_ENTERED',
                body={'values': updated_values}
            ).execute()
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "search_range": search_range,
                "find_text": find_text,
                "replace_text": replace_text,
                "updated_cells": updated_cells,
                "message": f"Successfully replaced '{find_text}' with '{replace_text}' in {updated_cells} cells"
            }
        else:
            return {
                "spreadsheet_id": spreadsheet_id,
                "search_range": search_range,
                "find_text": find_text,
                "replace_text": replace_text,
                "updated_cells": 0,
                "message": f"No instances of '{find_text}' found in range {search_range}"
            }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error performing find and replace: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error performing find and replace: {error}") 