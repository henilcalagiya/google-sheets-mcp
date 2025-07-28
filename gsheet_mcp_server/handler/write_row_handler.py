from typing import List, Any, Dict
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

class WriteRowRequest(BaseModel):
    """Request model for writing a row of data."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    row_range: str = Field(..., description="Row range (e.g., 'Sheet1!A1:Z1')")
    values: List[Any] = Field(..., description="List of values to write to the row")

class WriteRowResponse(BaseModel):
    """Response model for writing a row of data."""
    spreadsheet_name: str
    row_range: str
    updated_cells: int
    message: str

def write_row_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    row_range: str,
    values: List[Any]
) -> Dict[str, Any]:
    """
    Write a list of values to a row in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        row_range: Row range (e.g., 'Sheet1!A1:Z1')
        values: List of values to write to the row
    
    Returns:
        Dict containing write operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        # Convert list of values to 2D array format expected by API
        values_2d = [values]
        
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=row_range,
            valueInputOption='USER_ENTERED',
            body={'values': values_2d}
        ).execute()
        
        updated_cells = result.get('updatedCells', 0)
        updated_rows = result.get('updatedRows', 0)
        updated_columns = result.get('updatedColumns', 0)
        
        return {
            "spreadsheet_name": spreadsheet_name,
            "row_range": row_range,
            "updated_cells": updated_cells,
            "message": f"Successfully wrote {len(values)} values to row {row_range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error writing row data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error writing row data: {error}") 