from typing import List, Dict, Any, Optional, Union
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name

class WriteSheetRequest(BaseModel):
    """Request model for writing sheet data."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    ranges: List[str] = Field(..., description="List of ranges to update")
    values: List[List[List[Any]]] = Field(..., description="List of 2D arrays of values, one for each range")

class WriteSheetResponse(BaseModel):
    """Response model for writing sheet data."""
    spreadsheet_name: str
    range: str
    updated_cells: int
    updated_rows: int
    updated_columns: int
    message: str

class BatchUpdateResponse(BaseModel):
    """Response model for batch update operations."""
    spreadsheet_name: str
    results: List[Dict[str, Any]]
    total_ranges: int
    message: str



def write_sheet_data_with_ranges_and_values(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    ranges: List[str],
    values: List[List[List[Any]]]
) -> Dict[str, Any]:
    """
    Write data to multiple ranges using separate ranges and values lists.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        ranges: List of range strings (e.g., ['Sheet1!A1', 'Sheet1!B1'])
        values: List of 2D arrays of values, one for each range
    
    Returns:
        Dict containing results for all write operations
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    # Validate that ranges and values have the same length
    if len(ranges) != len(values):
        raise ValueError(f"Number of ranges ({len(ranges)}) must match number of values arrays ({len(values)})")
    
    # Convert to the format expected by write_multiple_ranges
    data = []
    for i, range_str in enumerate(ranges):
        data.append({
            "range": range_str,
            "values": values[i]
        })
    
    return write_multiple_ranges(
        sheets_service=sheets_service,
        spreadsheet_id=spreadsheet_id,
        data=data
    )

def write_multiple_ranges(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Write data to multiple ranges in a single API call.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        data: List of dicts with 'range' and 'values' keys
    
    Returns:
        Dict containing results for all write operations
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        # Prepare the batch update request
        data_body = []
        
        for item in data:
            data_body.append({
                'range': item['range'],
                'values': item['values']
            })
        
        result = sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'valueInputOption': 'USER_ENTERED',
                'data': data_body
            }
        ).execute()
        
        responses = result.get('responses', [])
        results = []
        
        for i, response in enumerate(responses):
            range_str = data[i]['range'] if i < len(data) else 'Unknown'
            updated_cells = response.get('updatedCells', 0)
            updated_rows = response.get('updatedRows', 0)
            updated_columns = response.get('updatedColumns', 0)
            
            results.append({
                "range": range_str,
                "updated_cells": updated_cells,
                "updated_rows": updated_rows,
                "updated_columns": updated_columns
            })
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "results": results,
            "total_ranges": len(results),
            "message": f"Successfully wrote to {len(results)} ranges"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error writing multiple ranges: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error writing multiple ranges: {error}")


def clear_sheet_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    range: str
) -> Dict[str, Any]:
    """
    Clear data from a specific range in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        range: Range to clear (e.g., 'Sheet1!A1:B10')
    
    Returns:
        Dict containing clear operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        result = sheets_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range,
            body={}
        ).execute()
        
        cleared_range = result.get('clearedRange', range)
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "cleared_range": cleared_range,
            "message": f"Successfully cleared range {cleared_range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error clearing sheet data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error clearing sheet data: {error}")


def append_sheet_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    range: str,
    values: List[List[Any]],
    insert_data_option: str = "INSERT_ROWS"
) -> Dict[str, Any]:
    """
    Append data to the end of a sheet or range.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        range: Range to append to (e.g., 'Sheet1!A:A')
        values: 2D array of values to append
        insert_data_option: How to handle data insertion
    
    Returns:
        Dict containing append operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            insertDataOption=insert_data_option,
            body={'values': values}
        ).execute()
        
        updated_cells = result.get('updates', {}).get('updatedCells', 0)
        updated_rows = result.get('updates', {}).get('updatedRows', 0)
        updated_columns = result.get('updates', {}).get('updatedColumns', 0)
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "range": range,
            "updated_cells": updated_cells,
            "updated_rows": updated_rows,
            "updated_columns": updated_columns,
            "message": f"Successfully appended {updated_cells} cells to {range}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error appending sheet data: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error appending sheet data: {error}")