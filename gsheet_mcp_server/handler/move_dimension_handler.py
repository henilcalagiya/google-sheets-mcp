from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

class MoveDimensionRequest(BaseModel):
    """Request model for moving rows or columns."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="The name of the sheet")
    dimension: str = Field(..., description="Dimension to move: 'ROWS' or 'COLUMNS'")
    source_start_index: int = Field(..., description="Starting index to move (0-based)")
    source_end_index: int = Field(..., description="Ending index to move (0-based, exclusive)")
    destination_index: int = Field(..., description="Destination index (0-based)")

class MoveDimensionResponse(BaseModel):
    """Response model for moving rows or columns."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    dimension: str
    source_start_index: int
    source_end_index: int
    destination_index: int
    items_moved: int
    message: str

def move_dimension(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    dimension: str,
    source_start_index: int,
    source_end_index: int,
    destination_index: int
) -> str:
    """
    Move rows or columns in a Google Sheet.
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
        dimension: Dimension to move ('ROWS' or 'COLUMNS')
        source_start_index: Starting index to move (0-based)
        source_end_index: Ending index to move (0-based, exclusive)
        destination_index: Destination index (0-based)
    
    Returns:
        Compact JSON string containing move operation results
    """
    
    # Validate input
    if not sheet_name:
        return compact_json_response({
            "success": False,
            "message": "No sheet name provided."
        })
    
    if dimension not in ['ROWS', 'COLUMNS']:
        return compact_json_response({
            "success": False,
            "message": "Dimension must be 'ROWS' or 'COLUMNS'."
        })
    
    if source_start_index >= source_end_index:
        return compact_json_response({
            "success": False,
            "message": "Source start index must be less than source end index."
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
        # Calculate number of items to move
        num_items = source_end_index - source_start_index
        
        # Prepare the batch update request
        request = {
            'moveDimension': {
                'source': {
                    'sheetId': sheet_id,
                    'dimension': dimension,
                    'startIndex': source_start_index,
                    'endIndex': source_end_index
                },
                'destinationIndex': destination_index
            }
        }
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "sheet_id": sheet_id,
            "dimension": dimension,
            "source_start_index": source_start_index,
            "source_end_index": source_end_index,
            "destination_index": destination_index,
            "items_moved": num_items,
            "message": f"Successfully moved {num_items} {dimension.lower()} from position {source_start_index}-{source_end_index} to position {destination_index} in sheet '{sheet_name}'."
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error moving {dimension.lower()}: {error}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {error}"
        }) 