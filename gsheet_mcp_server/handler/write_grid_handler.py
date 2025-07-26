from typing import List, Any, Dict
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class WriteGridRequest(BaseModel):
    """Request model for writing a grid of data."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    grid_range: str = Field(..., description="Grid range (e.g., 'Sheet1!A1:C10')")
    values: List[List[Any]] = Field(..., description="2D array of values to write to the grid")

class WriteGridResponse(BaseModel):
    """Response model for writing a grid of data."""
    spreadsheet_id: str
    grid_range: str
    updated_cells: int
    updated_rows: int
    updated_columns: int
    message: str

def write_grid_data(
    sheets_service,
    spreadsheet_id: str,
    grid_range: str,
    values: List[List[Any]]
) -> Dict[str, Any]:
    """
    Write a 2D array of values to a grid range in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        grid_range: Grid range (e.g., 'Sheet1!A1:C10')
        values: 2D array of values to write to the grid
    
    Returns:
        Dict containing write operation results
    """
    
    try:
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=grid_range,
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
        
        updated_cells = result.get('updatedCells', 0)
        updated_rows = result.get('updatedRows', 0)
        updated_columns = result.get('updatedColumns', 0)
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "grid_range": grid_range,
            "updated_cells": updated_cells,
            "updated_rows": updated_rows,
            "updated_columns": updated_columns,
            "message": f"Successfully wrote {len(values)} rows to grid {grid_range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error writing grid data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error writing grid data: {error}") 