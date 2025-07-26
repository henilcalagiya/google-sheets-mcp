from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class MoveRowsRequest(BaseModel):
    """Request model for moving rows."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    source_start_index: int = Field(..., description="Starting row index to move (0-based)")
    source_end_index: int = Field(..., description="Ending row index to move (0-based, exclusive)")
    destination_index: int = Field(..., description="Destination row index (0-based)")

class MoveRowsResponse(BaseModel):
    """Response model for moving rows."""
    spreadsheet_id: str
    sheet_id: int
    source_start_index: int
    source_end_index: int
    destination_index: int
    moved_rows: int
    message: str

def move_rows_data(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    source_start_index: int,
    source_end_index: int,
    destination_index: int
) -> Dict[str, Any]:
    """
    Move rows in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        source_start_index: Starting row index to move (0-based)
        source_end_index: Ending row index to move (0-based, exclusive)
        destination_index: Destination row index (0-based)
    
    Returns:
        Dict containing move operation results
    """
    
    try:
        # Calculate number of rows to move
        num_rows = source_end_index - source_start_index
        
        # Prepare the batch update request
        request = {
            'moveDimension': {
                'source': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': source_start_index,
                    'endIndex': source_end_index
                },
                'destinationIndex': destination_index
            }
        }
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_id": sheet_id,
            "source_start_index": source_start_index,
            "source_end_index": source_end_index,
            "destination_index": destination_index,
            "moved_rows": num_rows,
            "message": f"Successfully moved {num_rows} rows from index {source_start_index} to {destination_index}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error moving rows: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error moving rows: {error}") 