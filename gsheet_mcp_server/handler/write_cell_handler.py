from typing import Any, Dict
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

class WriteCellRequest(BaseModel):
    """Request model for writing a single cell."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    cell: str = Field(..., description="Cell reference (e.g., 'Sheet1!A1')")
    value: Any = Field(..., description="Value to write to the cell")

class WriteCellResponse(BaseModel):
    """Response model for writing a single cell."""
    spreadsheet_id: str
    cell: str
    updated_cells: int
    message: str

def write_cell_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    cell: str,
    value: Any
) -> Dict[str, Any]:
    """
    Write a single value to a specific cell in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        cell: Cell reference (e.g., 'Sheet1!A1')
        value: Value to write to the cell
    
    Returns:
        Dict containing write operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        # Convert single value to 2D array format expected by API
        values = [[value]]
        
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=cell,
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
        
        updated_cells = result.get('updatedCells', 0)
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "cell": cell,
            "updated_cells": updated_cells,
            "message": f"Successfully wrote value to {cell}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error writing cell data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error writing cell data: {error}") 