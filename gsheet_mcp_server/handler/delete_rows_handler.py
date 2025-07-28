from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names

class DeleteRowsRequest(BaseModel):
    """Request model for deleting rows."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="The name of the sheet")
    row_indices: List[int] = Field(..., description="List of row indices to delete (0-based)")

class DeleteRowsResponse(BaseModel):
    """Response model for deleting rows."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    deleted_rows: List[int]
    rows_deleted: int
    message: str

def delete_rows_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    row_indices: List[int]
) -> Dict[str, Any]:
    """
    Delete specific rows from a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
        row_indices: List of row indices to delete (0-based)
    
    Returns:
        Dict containing delete operation results
    """
    
    # Validate input
    if not sheet_name:
        return {
            "success": False,
            "message": "No sheet name provided."
        }
    
    if not row_indices:
        return {
            "success": False,
            "message": "No row indices provided."
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
        sorted_indices = sorted(row_indices, reverse=True)
        
        # Prepare batch update requests
        requests = []
        for row_index in sorted_indices:
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': row_index,
                        'endIndex': row_index + 1
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
            "deleted_rows": row_indices,
            "rows_deleted": len(row_indices),
            "message": f"Successfully deleted {len(row_indices)} rows from sheet '{sheet_name}'"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        return {
            "success": False,
            "message": f"Error deleting rows: {error_message}"
        }
    except Exception as error:
        return {
            "success": False,
            "message": f"Unexpected error deleting rows: {error}"
        } 