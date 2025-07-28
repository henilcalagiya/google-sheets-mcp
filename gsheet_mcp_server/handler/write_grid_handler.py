from typing import List, Any, Dict
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

class WriteGridRequest(BaseModel):
    """Request model for writing a grid of data."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    grid_range: str = Field(..., description="Grid range (e.g., 'Sheet1!A1:C10')")
    values: List[List[Any]] = Field(..., description="2D array of values to write to the grid")

class WriteGridResponse(BaseModel):
    """Response model for writing a grid of data."""
    spreadsheet_name: str
    grid_range: str
    updated_cells: int
    message: str

def write_grid_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    grid_range: str,
    values: List[List[Any]]
) -> Dict[str, Any]:
    """
    Write a 2D array of values to a grid range in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        grid_range: Grid range (e.g., 'Sheet1!A1:C10')
        values: 2D array of values to write to the grid
    
    Returns:
        Dict containing write operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
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
            "spreadsheet_name": spreadsheet_name,
            "grid_range": grid_range,
            "updated_cells": updated_cells,
            "message": f"Successfully wrote grid data to {grid_range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error writing grid data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error writing grid data: {error}") 