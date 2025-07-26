from typing import Dict, Any
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class MergeCellsRequest(BaseModel):
    """Request model for merging cells."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    start_row_index: int = Field(..., description="Starting row index (0-based)")
    end_row_index: int = Field(..., description="Ending row index (0-based, exclusive)")
    start_column_index: int = Field(..., description="Starting column index (0-based)")
    end_column_index: int = Field(..., description="Ending column index (0-based, exclusive)")
    merge_type: str = Field(default="MERGE_ALL", description="Merge type: MERGE_ALL, MERGE_COLUMNS, MERGE_ROWS")

class MergeCellsResponse(BaseModel):
    """Response model for merging cells."""
    spreadsheet_id: str
    sheet_id: int
    merged_range: str
    merge_type: str
    message: str

def merge_cells_data(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    start_row_index: int,
    end_row_index: int,
    start_column_index: int,
    end_column_index: int,
    merge_type: str = "MERGE_ALL"
) -> Dict[str, Any]:
    """
    Merge cells in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        start_row_index: Starting row index (0-based)
        end_row_index: Ending row index (0-based, exclusive)
        start_column_index: Starting column index (0-based)
        end_column_index: Ending column index (0-based, exclusive)
        merge_type: Type of merge operation
    
    Returns:
        Dict containing merge operation results
    """
    
    try:
        # Validate merge type
        valid_merge_types = ["MERGE_ALL", "MERGE_COLUMNS", "MERGE_ROWS"]
        if merge_type not in valid_merge_types:
            raise ValueError(f"Invalid merge type. Must be one of: {valid_merge_types}")
        
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
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_id": sheet_id,
            "merged_range": f"Rows {start_row_index}-{end_row_index-1}, Columns {start_column_index}-{end_column_index-1}",
            "merge_type": merge_type,
            "message": f"Successfully merged cells in range {start_row_index}:{end_row_index-1}, {start_column_index}:{end_column_index-1} using {merge_type}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error merging cells: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error merging cells: {error}") 