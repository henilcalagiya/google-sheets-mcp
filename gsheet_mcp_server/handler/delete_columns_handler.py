from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

class DeleteColumnsRequest(BaseModel):
    """Request model for deleting columns."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    column_indices: List[int] = Field(..., description="List of column indices to delete (0-based)")

class DeleteColumnsResponse(BaseModel):
    """Response model for deleting columns."""
    spreadsheet_name: str
    sheet_id: int
    deleted_columns: List[int]
    columns_deleted: int
    message: str

def delete_columns_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_id: int,
    column_indices: List[int]
) -> Dict[str, Any]:
    """
    Delete specific columns from a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        column_indices: List of column indices to delete (0-based)
    
    Returns:
        Dict containing delete operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
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
            "spreadsheet_name": spreadsheet_name,
            "sheet_id": sheet_id,
            "deleted_columns": column_indices,
            "columns_deleted": len(column_indices),
            "message": f"Successfully deleted {len(column_indices)} columns"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error deleting columns: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error deleting columns: {error}") 