from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

class ResizeColumnsRequest(BaseModel):
    """Request model for resizing columns."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    column_indices: List[int] = Field(..., description="List of column indices to resize (0-based)")
    widths: List[int] = Field(..., description="List of widths in pixels for each column")

class ResizeColumnsResponse(BaseModel):
    """Response model for resizing columns."""
    spreadsheet_id: str
    sheet_id: int
    column_indices: List[int]
    widths: List[int]
    resized_columns: int
    message: str

def resize_columns_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_id: int,
    column_indices: List[int],
    widths: List[int]
) -> Dict[str, Any]:
    """
    Resize columns in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        column_indices: List of column indices to resize (0-based)
        widths: List of widths in pixels for each column
    
    Returns:
        Dict containing resize operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        # Validate that column_indices and widths have the same length
        if len(column_indices) != len(widths):
            raise ValueError("Number of column indices must match number of widths")
        
        # Prepare the batch update request
        requests = []
        for i, column_index in enumerate(column_indices):
            request = {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': column_index,
                        'endIndex': column_index + 1
                    },
                    'properties': {
                        'pixelSize': widths[i]
                    },
                    'fields': 'pixelSize'
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
            "widths": widths,
            "resized_columns": len(column_indices),
            "message": f"Successfully resized {len(column_indices)} columns"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error resizing columns: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error resizing columns: {error}") 