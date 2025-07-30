from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

class ResizeColumnsRequest(BaseModel):
    """Request model for resizing columns."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="The name of the sheet")
    column_indices: List[int] = Field(..., description="List of column indices to resize (0-based)")
    widths: List[int] = Field(..., description="List of widths in pixels for each column")

class ResizeColumnsResponse(BaseModel):
    """Response model for resizing columns."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    column_indices: List[int]
    widths: List[int]
    columns_resized: int
    message: str

def resize_columns_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    column_indices: List[int],
    widths: List[int]
) -> str:
    """
    Resize columns in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
        column_indices: List of column indices to resize (0-based)
        widths: List of widths in pixels for each column
    
    Returns:
        Compact JSON string containing resize operation results
    """
    
    # Validate input
    if not sheet_name:
        return compact_json_response({
            "success": False,
            "message": "No sheet name provided."
        })
    
    if not column_indices:
        return compact_json_response({
            "success": False,
            "message": "No column indices provided."
        })
    
    if not widths:
        return compact_json_response({
            "success": False,
            "message": "No widths provided."
        })
    
    # Validate that column_indices and widths have the same length
    if len(column_indices) != len(widths):
        return compact_json_response({
            "success": False,
            "message": f"Number of column indices ({len(column_indices)}) must match number of widths ({len(widths)})"
        })
    
    # Get spreadsheet ID
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    # Get sheet ID from sheet name
    sheet_id_map = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
    sheet_id = sheet_id_map.get(sheet_name)
    
    if sheet_id is None:
        return compact_json_response({
            "success": False,
            "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
        })
    
    try:
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
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "column_indices": column_indices,
            "widths": widths,
            "columns_resized": len(column_indices),
            "message": f"Successfully resized {len(column_indices)} columns in sheet '{sheet_name}'"
        })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        return compact_json_response({
            "success": False,
            "message": f"Error resizing columns: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error resizing columns: {error}"
        }) 