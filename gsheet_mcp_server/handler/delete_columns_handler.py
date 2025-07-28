from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names

class DeleteColumnsRequest(BaseModel):
    """Request model for deleting columns."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="The name of the sheet")
    column_indices: List[int] = Field(..., description="List of column indices to delete (0-based)")

class DeleteColumnsResponse(BaseModel):
    """Response model for deleting columns."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    deleted_columns: List[int]
    columns_deleted: int
    message: str

def delete_columns_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    column_indices: List[int]
) -> Dict[str, Any]:
    """
    Delete specific columns from a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
        column_indices: List of column indices to delete (0-based)
    
    Returns:
        Dict containing delete operation results
    """
    
    # Validate input
    if not sheet_name:
        return {
            "success": False,
            "message": "No sheet name provided."
        }
    
    if not column_indices:
        return {
            "success": False,
            "message": "No column indices provided."
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
        # Sort indices in descending order to avoid shifting issues
        sorted_indices = sorted(column_indices, reverse=True)
        
        # Prepare batch update requests
        requests = []
        for column_index in sorted_indices:
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': column_index,
                        'endIndex': column_index + 1
                    }
                }
            }
            requests.append(request)
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "deleted_columns": column_indices,
            "columns_deleted": len(column_indices),
            "message": f"Successfully deleted {len(column_indices)} columns from sheet '{sheet_name}'"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        return {
            "success": False,
            "message": f"Error deleting columns: {error_message}"
        }
    except Exception as error:
        return {
            "success": False,
            "message": f"Unexpected error deleting columns: {error}"
        } 