from typing import Dict, Any, List, Optional
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class ConditionalFormatRequest(BaseModel):
    """Request model for conditional formatting."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    start_row_index: int = Field(..., description="Starting row index (0-based)")
    end_row_index: int = Field(..., description="Ending row index (0-based, exclusive)")
    start_column_index: int = Field(..., description="Starting column index (0-based)")
    end_column_index: int = Field(..., description="Ending column index (0-based, exclusive)")
    rule_type: str = Field(..., description="Rule type: NUMBER_GREATER_THAN, NUMBER_LESS_THAN, TEXT_CONTAINS, etc.")
    condition_value: Any = Field(..., description="Value to compare against")
    background_color: Optional[Dict[str, float]] = Field(default=None, description="Background color RGB values (0-1)")
    text_color: Optional[Dict[str, float]] = Field(default=None, description="Text color RGB values (0-1)")
    bold: Optional[bool] = Field(default=None, description="Whether text is bold")
    italic: Optional[bool] = Field(default=None, description="Whether text is italic")

class ConditionalFormatResponse(BaseModel):
    """Response model for conditional formatting."""
    spreadsheet_id: str
    sheet_id: int
    formatted_range: str
    rule_type: str
    message: str

def conditional_format_data(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    start_row_index: int,
    end_row_index: int,
    start_column_index: int,
    end_column_index: int,
    rule_type: str,
    condition_value: Any,
    background_color: Optional[Dict[str, float]] = None,
    text_color: Optional[Dict[str, float]] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Apply conditional formatting to cells in a Google Sheet.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        start_row_index: Starting row index (0-based)
        end_row_index: Ending row index (0-based, exclusive)
        start_column_index: Starting column index (0-based)
        end_column_index: Ending column index (0-based, exclusive)
        rule_type: Type of conditional formatting rule
        condition_value: Value to compare against
        background_color: Background color RGB values (0-1)
        text_color: Text color RGB values (0-1)
        bold: Whether text is bold
        italic: Whether text is italic
    
    Returns:
        Dict containing conditional format operation results
    """
    
    try:
        # Prepare the cell format
        cell_format = {}
        
        if background_color:
            cell_format['backgroundColor'] = background_color
        
        if text_color or bold is not None or italic is not None:
            cell_format['textFormat'] = {}
            if text_color:
                cell_format['textFormat']['foregroundColor'] = text_color
            if bold is not None:
                cell_format['textFormat']['bold'] = bold
            if italic is not None:
                cell_format['textFormat']['italic'] = italic
        
        # Prepare the condition
        condition = {
            'type': rule_type,
            'values': [{'userEnteredValue': str(condition_value)}]
        }
        
        # Prepare the conditional format rule
        rule = {
            'ranges': [{
                'sheetId': sheet_id,
                'startRowIndex': start_row_index,
                'endRowIndex': end_row_index,
                'startColumnIndex': start_column_index,
                'endColumnIndex': end_column_index
            }],
            'booleanRule': {
                'condition': condition,
                'format': cell_format
            }
        }
        
        # Prepare the batch update request
        request = {
            'addConditionalFormatRule': {
                'rule': rule
            }
        }
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_id": sheet_id,
            "formatted_range": f"Rows {start_row_index}-{end_row_index-1}, Columns {start_column_index}-{end_column_index-1}",
            "rule_type": rule_type,
            "message": f"Successfully applied conditional formatting rule '{rule_type}' to range {start_row_index}:{end_row_index-1}, {start_column_index}:{end_column_index-1}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error applying conditional formatting: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error applying conditional formatting: {error}") 