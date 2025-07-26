from typing import Dict, Any, List, Optional
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class FormatCellsRequest(BaseModel):
    """Request model for formatting cells."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)")
    start_row_index: int = Field(..., description="Starting row index (0-based)")
    end_row_index: int = Field(..., description="Ending row index (0-based, exclusive)")
    start_column_index: int = Field(..., description="Starting column index (0-based)")
    end_column_index: int = Field(..., description="Ending column index (0-based, exclusive)")
    background_color: Optional[Dict[str, float]] = Field(default=None, description="Background color RGB values (0-1)")
    text_color: Optional[Dict[str, float]] = Field(default=None, description="Text color RGB values (0-1)")
    font_family: Optional[str] = Field(default=None, description="Font family name")
    font_size: Optional[int] = Field(default=None, description="Font size in points")
    bold: Optional[bool] = Field(default=None, description="Whether text is bold")
    italic: Optional[bool] = Field(default=None, description="Whether text is italic")
    underline: Optional[bool] = Field(default=None, description="Whether text is underlined")
    horizontal_alignment: Optional[str] = Field(default=None, description="Horizontal alignment: LEFT, CENTER, RIGHT")
    vertical_alignment: Optional[str] = Field(default=None, description="Vertical alignment: TOP, MIDDLE, BOTTOM")
    borders: Optional[Dict[str, Any]] = Field(default=None, description="Border styling")

class FormatCellsResponse(BaseModel):
    """Response model for formatting cells."""
    spreadsheet_id: str
    sheet_id: int
    formatted_range: str
    message: str

def format_cells_data(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    start_row_index: int,
    end_row_index: int,
    start_column_index: int,
    end_column_index: int,
    background_color: Optional[Dict[str, float]] = None,
    text_color: Optional[Dict[str, float]] = None,
    font_family: Optional[str] = None,
    font_size: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    underline: Optional[bool] = None,
    horizontal_alignment: Optional[str] = None,
    vertical_alignment: Optional[str] = None,
    borders: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format cells in a Google Sheet with various styling options.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet (0-based)
        start_row_index: Starting row index (0-based)
        end_row_index: Ending row index (0-based, exclusive)
        start_column_index: Starting column index (0-based)
        end_column_index: Ending column index (0-based, exclusive)
        background_color: Background color RGB values (0-1)
        text_color: Text color RGB values (0-1)
        font_family: Font family name
        font_size: Font size in points
        bold: Whether text is bold
        italic: Whether text is italic
        underline: Whether text is underlined
        horizontal_alignment: Horizontal alignment
        vertical_alignment: Vertical alignment
        borders: Border styling
    
    Returns:
        Dict containing format operation results
    """
    
    try:
        # Prepare the cell format
        cell_format = {}
        
        if background_color:
            cell_format['backgroundColor'] = background_color
        
        if text_color or font_family or font_size or bold is not None or italic is not None or underline is not None:
            cell_format['textFormat'] = {}
            if text_color:
                cell_format['textFormat']['foregroundColor'] = text_color
            if font_family:
                cell_format['textFormat']['fontFamily'] = font_family
            if font_size:
                cell_format['textFormat']['fontSize'] = font_size
            if bold is not None:
                cell_format['textFormat']['bold'] = bold
            if italic is not None:
                cell_format['textFormat']['italic'] = italic
            if underline is not None:
                cell_format['textFormat']['underline'] = underline
        
        if horizontal_alignment or vertical_alignment:
            cell_format['horizontalAlignment'] = horizontal_alignment
            cell_format['verticalAlignment'] = vertical_alignment
        
        if borders:
            cell_format['borders'] = borders
        
        # Prepare the batch update request
        request = {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': start_row_index,
                    'endRowIndex': end_row_index,
                    'startColumnIndex': start_column_index,
                    'endColumnIndex': end_column_index
                },
                'cell': {
                    'userEnteredFormat': cell_format
                },
                'fields': 'userEnteredFormat'
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
            "message": f"Successfully formatted cells in range {start_row_index}:{end_row_index-1}, {start_column_index}:{end_column_index-1}"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error formatting cells: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error formatting cells: {error}") 