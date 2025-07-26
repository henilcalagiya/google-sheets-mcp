from typing import List, Any, Dict
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class AppendDataRequest(BaseModel):
    """Request model for appending data to a column."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    column_range: str = Field(..., description="Column range (e.g., 'Sheet1!A:A')")
    values: List[Any] = Field(..., description="List of values to append to the column")

class AppendDataResponse(BaseModel):
    """Response model for appending data to a column."""
    spreadsheet_id: str
    column_range: str
    updated_cells: int
    updated_rows: int
    updated_columns: int
    message: str

def append_data_to_column(
    sheets_service,
    spreadsheet_id: str,
    column_range: str,
    values: List[Any]
) -> Dict[str, Any]:
    """
    Append a list of values to the end of a column in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        column_range: Column range (e.g., 'Sheet1!A:A')
        values: List of values to append to the column
    
    Returns:
        Dict containing append operation results
    """
    
    try:
        # Convert list of values to 2D array format expected by API
        # Each value becomes a row with one column
        values_2d = [[value] for value in values]
        
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=column_range,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': values_2d}
        ).execute()
        
        updated_cells = result.get('updates', {}).get('updatedCells', 0)
        updated_rows = result.get('updates', {}).get('updatedRows', 0)
        updated_columns = result.get('updates', {}).get('updatedColumns', 0)
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "column_range": column_range,
            "updated_cells": updated_cells,
            "updated_rows": updated_rows,
            "updated_columns": updated_columns,
            "message": f"Successfully appended {len(values)} values to column {column_range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error appending data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error appending data: {error}") 