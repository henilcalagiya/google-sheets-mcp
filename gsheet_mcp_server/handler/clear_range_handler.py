from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class ClearRangeRequest(BaseModel):
    """Request model for clearing a range."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    range: str = Field(..., description="Range to clear (e.g., 'Sheet1!A1:B10')")

class ClearRangeResponse(BaseModel):
    """Response model for clearing a range."""
    spreadsheet_id: str
    cleared_range: str
    message: str

def clear_range_data(
    sheets_service,
    spreadsheet_id: str,
    range: str
) -> Dict[str, Any]:
    """
    Clear data from a specific range in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        range: Range to clear (e.g., 'Sheet1!A1:B10')
    
    Returns:
        Dict containing clear operation results
    """
    
    try:
        result = sheets_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range,
            body={}
        ).execute()
        
        cleared_range = result.get('clearedRange', range)
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "cleared_range": cleared_range,
            "message": f"Successfully cleared range {cleared_range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error clearing range: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error clearing range: {error}") 