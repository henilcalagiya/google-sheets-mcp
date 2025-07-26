from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class DeleteColumnsRequest(BaseModel):
    """Request model for deleting columns."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    column_indices: List[int] = Field(..., description="List of column indices to delete (0-based)")

class DeleteColumnsResponse(BaseModel):
    """Response model for deleting columns."""
    spreadsheet_id: str
    sheet_id: int
    column_indices: List[int]
    deleted_columns: int
    message: str

def delete_columns_data(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    column_indices: List[int]
) -> Dict[str, Any]:
    """
    Delete specific columns from a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        column_indices: List of column indices to delete (0-based)
    
    Returns:
        Dict containing delete operation results
    """
    
    try:
        # Sort indices in descending order to avoid shifting issues
        sorted_indices = sorted(column_indices, reverse=True)
        
        # Prepare batch update requests
        requests = []
        for column_index in sorted_indices:
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': column_index,
                        'endIndex': column_index + 1
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
            "column_indices": column_indices,
            "deleted_columns": len(column_indices),
            "message": f"Successfully deleted {len(column_indices)} columns: {column_indices}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error deleting columns: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error deleting columns: {error}") 