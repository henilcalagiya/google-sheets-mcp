from typing import List, Any, Dict
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class WriteRowRequest(BaseModel):
    """Request model for writing a row of data."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    row_range: str = Field(..., description="Row range (e.g., 'Sheet1!A1:Z1')")
    values: List[Any] = Field(..., description="List of values to write to the row")

class WriteRowResponse(BaseModel):
    """Response model for writing a row of data."""
    spreadsheet_id: str
    row_range: str
    updated_cells: int
    updated_rows: int
    updated_columns: int
    message: str

def write_row_data(
    sheets_service,
    spreadsheet_id: str,
    row_range: str,
    values: List[Any]
) -> Dict[str, Any]:
    """
    Write a list of values to a row in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        row_range: Row range (e.g., 'Sheet1!A1:Z1')
        values: List of values to write to the row
    
    Returns:
        Dict containing write operation results
    """
    
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
            "spreadsheet_id": spreadsheet_id,
            "row_range": row_range,
            "updated_cells": updated_cells,
            "updated_rows": updated_rows,
            "updated_columns": updated_columns,
            "message": f"Successfully wrote {len(values)} values to row {row_range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error writing row data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error writing row data: {error}") 