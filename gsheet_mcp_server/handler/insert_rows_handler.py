from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class InsertRowsRequest(BaseModel):
    """Request model for inserting rows."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    start_index: int = Field(..., description="Starting row index (0-based)")
    end_index: int = Field(..., description="Ending row index (0-based, exclusive)")

class InsertRowsResponse(BaseModel):
    """Response model for inserting rows."""
    spreadsheet_id: str
    sheet_id: int
    start_index: int
    end_index: int
    inserted_rows: int
    message: str

def insert_rows_data(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    start_index: int,
    end_index: int
) -> Dict[str, Any]:
    """
    Insert rows in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        start_index: Starting row index (0-based)
        end_index: Ending row index (0-based, exclusive)
    
    Returns:
        Dict containing insert operation results
    """
    
    try:
        # Calculate number of rows to insert
        num_rows = end_index - start_index
        
        # Prepare the batch update request
        request = {
            'insertDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'inheritFromBefore': True
            }
        }
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_id": sheet_id,
            "start_index": start_index,
            "end_index": end_index,
            "inserted_rows": num_rows,
            "message": f"Successfully inserted {num_rows} rows starting at index {start_index}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error inserting rows: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error inserting rows: {error}") 