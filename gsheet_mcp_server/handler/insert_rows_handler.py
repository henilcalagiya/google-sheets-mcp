from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names

class InsertRowsRequest(BaseModel):
    """Request model for inserting rows."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="The name of the sheet")
    start_index: int = Field(..., description="Starting row index (0-based)")
    end_index: int = Field(..., description="Ending row index (0-based, exclusive)")

class InsertRowsResponse(BaseModel):
    """Response model for inserting rows."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    start_index: int
    end_index: int
    rows_inserted: int
    message: str

def insert_rows_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    start_index: int,
    end_index: int
) -> Dict[str, Any]:
    """
    Insert rows in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
        start_index: Starting row index (0-based)
        end_index: Ending row index (0-based, exclusive)
    
    Returns:
        Dict containing insert operation results
    """
    
    # Validate input
    if not sheet_name:
        return {
            "success": False,
            "message": "No sheet name provided."
        }
    
    # Get spreadsheet ID
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return {
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        }
    
    # Get sheet ID from sheet name
    sheet_id_map = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
    sheet_id = sheet_id_map.get(sheet_name)
    
    if sheet_id is None:
        return {
            "success": False,
            "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
        }
    
    try:
        # Calculate number of rows to insert
        num_rows = end_index - start_index
        
        # Prepare the batch update request
        request = {
            'insertDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'inheritFromBefore': True
            }
        }
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "start_index": start_index,
            "end_index": end_index,
            "rows_inserted": num_rows,
            "message": f"Successfully inserted {num_rows} rows starting at index {start_index} in sheet '{sheet_name}'"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        return {
            "success": False,
            "message": f"Error inserting rows: {error_message}"
        }
    except Exception as error:
        return {
            "success": False,
            "message": f"Unexpected error inserting rows: {error}"
        } 