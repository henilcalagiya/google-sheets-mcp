from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

class DeleteDimensionRequest(BaseModel):
    """Request model for deleting rows or columns."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="The name of the sheet")
    dimension: str = Field(..., description="Dimension to delete: 'ROWS' or 'COLUMNS'")
    indices: List[int] = Field(..., description="List of row/column indices to delete (0-based)")

class DeleteDimensionResponse(BaseModel):
    """Response model for deleting rows or columns."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    deleted_indices: List[int]
    items_deleted: int
    dimension: str
    message: str

def delete_dimension(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    dimension: str,
    indices: List[int]
) -> str:
    """
    Delete specific rows or columns from a Google Sheet.
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
        dimension: Dimension to delete ('ROWS' or 'COLUMNS')
        indices: List of row/column indices to delete (0-based)
    
    Returns:
        Compact JSON string containing delete operation results
    """
    
    # Validate input
    if not sheet_name:
        return compact_json_response({
            "success": False,
            "message": "No sheet name provided."
        })
    
    if not indices:
        return compact_json_response({
            "success": False,
            "message": "No indices provided."
        })
    
    if dimension not in ['ROWS', 'COLUMNS']:
        return compact_json_response({
            "success": False,
            "message": "Dimension must be 'ROWS' or 'COLUMNS'."
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
        # Sort indices in descending order to avoid shifting issues
        sorted_indices = sorted(indices, reverse=True)
        
        # Prepare batch update requests
        requests = []
        for index in sorted_indices:
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': dimension,
                        'startIndex': index,
                        'endIndex': index + 1
                    }
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
            "sheet_id": sheet_id,
            "deleted_indices": indices,
            "items_deleted": len(indices),
            "dimension": dimension,
            "message": f"Successfully deleted {len(indices)} {dimension.lower()} from sheet '{sheet_name}'."
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error deleting {dimension.lower()}: {error}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {error}"
        }) 