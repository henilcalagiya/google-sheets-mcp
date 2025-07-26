from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class DeleteRowsRequest(BaseModel):
    """Request model for deleting rows."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    row_indices: List[int] = Field(..., description="List of row indices to delete (0-based)")

class DeleteRowsResponse(BaseModel):
    """Response model for deleting rows."""
    spreadsheet_id: str
    sheet_id: int
    row_indices: List[int]
    deleted_rows: int
    message: str

def delete_rows_data(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    row_indices: List[int]
) -> Dict[str, Any]:
    """
    Delete specific rows from a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        row_indices: List of row indices to delete (0-based)
    
    Returns:
        Dict containing delete operation results
    """
    
    try:
        # Sort indices in descending order to avoid shifting issues
        sorted_indices = sorted(row_indices, reverse=True)
        
        # Prepare batch update requests
        requests = []
        for row_index in sorted_indices:
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': row_index,
                        'endIndex': row_index + 1
                    }
                }
            }
            requests.append(request)
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_id": sheet_id,
            "row_indices": row_indices,
            "deleted_rows": len(row_indices),
            "message": f"Successfully deleted {len(row_indices)} rows: {row_indices}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error deleting rows: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error deleting rows: {error}") 