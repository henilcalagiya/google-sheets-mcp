from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response

class MergeCellsRequest(BaseModel):
    """Request model for merging cells."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    start_row_index: int = Field(..., description="Starting row index (0-based)")
    end_row_index: int = Field(..., description="Ending row index (0-based, exclusive)")
    start_column_index: int = Field(..., description="Starting column index (0-based)")
    end_column_index: int = Field(..., description="Ending column index (0-based, exclusive)")
    merge_type: str = Field(default="MERGE_ALL", description="Merge type: MERGE_ALL, MERGE_COLUMNS, MERGE_ROWS")

class MergeCellsResponse(BaseModel):
    """Response model for merging cells."""
    spreadsheet_name: str
    sheet_id: int
    merge_type: str
    range: str
    cells_merged: int
    message: str

def merge_cells_data(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_id: int,
    start_row_index: int,
    end_row_index: int,
    start_column_index: int,
    end_column_index: int,
    merge_type: str = "MERGE_ALL"
) -> str:
    """
    Merge cells in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        start_row_index: Starting row index (0-based)
        end_row_index: Ending row index (0-based, exclusive)
        start_column_index: Starting column index (0-based)
        end_column_index: Ending column index (0-based, exclusive)
        merge_type: Type of merge operation
    
    Returns:
        Compact JSON string containing merge operation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        # Validate merge type
        valid_merge_types = ["MERGE_ALL", "MERGE_COLUMNS", "MERGE_ROWS"]
        if merge_type not in valid_merge_types:
            return compact_json_response({
                "success": False,
                "message": f"Invalid merge type. Must be one of: {valid_merge_types}"
            })
        
        # Prepare the batch update request
        request = {
            'mergeCells': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': start_row_index,
                    'endRowIndex': end_row_index,
                    'startColumnIndex': start_column_index,
                    'endColumnIndex': end_column_index
                },
                'mergeType': merge_type
            }
        }
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_id": sheet_id,
            "merge_type": merge_type,
            "range": f"Rows {start_row_index}-{end_row_index-1}, Columns {start_column_index}-{end_column_index-1}",
            "cells_merged": (end_row_index - start_row_index) * (end_column_index - start_column_index),
            "message": f"Successfully merged cells in range {start_row_index}:{end_row_index-1}, {start_column_index}:{end_column_index-1}"
        })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        return compact_json_response({
            "success": False,
            "message": f"Error merging cells: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error merging cells: {error}"
        }) 