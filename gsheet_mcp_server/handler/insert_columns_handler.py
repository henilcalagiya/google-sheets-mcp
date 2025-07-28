from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names

class InsertColumnsRequest(BaseModel):
    """Request model for inserting columns."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="The name of the sheet")
    start_index: int = Field(..., description="Starting column index (0-based)")
    end_index: int = Field(..., description="Ending column index (0-based, exclusive)")

class InsertColumnsResponse(BaseModel):
    """Response model for inserting columns."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    start_index: int
    end_index: int
    columns_inserted: int
    message: str

def insert_columns_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    start_index: int,
    end_index: int
) -> Dict[str, Any]:
    """
    Insert columns in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
        start_index: Starting column index (0-based)
        end_index: Ending column index (0-based, exclusive)
    
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
        # Calculate number of columns to insert
        num_columns = end_index - start_index
        
        # Prepare the batch update request
        request = {
            'insertDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
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
            "columns_inserted": num_columns,
            "message": f"Successfully inserted {num_columns} columns starting at index {start_index} in sheet '{sheet_name}'"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        return {
            "success": False,
            "message": f"Error inserting columns: {error_message}"
        }
    except Exception as error:
        return {
            "success": False,
            "message": f"Unexpected error inserting columns: {error}"
        } 