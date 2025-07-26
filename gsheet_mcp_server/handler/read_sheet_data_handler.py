from typing import List, Dict, Any, Optional, Union
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class ReadSheetRequest(BaseModel):
    """Request model for reading sheet data."""
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet to read")
    read_type: str = Field(..., description="Type of reading: 'column', 'row', or 'custom'")
    range_spec: str = Field(..., description="Range specification based on read_type")
    value_render_option: str = Field(default="FORMATTED_VALUE", description="How to render values")
    date_time_render_option: str = Field(default="FORMATTED_STRING", description="How to render dates")

class ReadSheetResponse(BaseModel):
    """Response model for reading sheet data."""
    spreadsheet_id: str
    sheet_name: str
    range: str
    values: List[List[str]]
    row_count: int
    column_count: int
    message: str



def read_multiple_ranges(
    sheets_service,
    spreadsheet_id: str,
    ranges: List[str],
    value_render_option: str = "FORMATTED_VALUE",
    date_time_render_option: str = "FORMATTED_STRING"
) -> Dict[str, Any]:
    """
    Read multiple ranges from a spreadsheet in a single API call.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        ranges: List of range strings (e.g., ['Sheet1!A1:B10', 'Sheet2!A:A'])
        value_render_option: How to render values
        date_time_render_option: How to render dates
    
    Returns:
        Dict containing data for all requested ranges
    """
    
    try:
        result = sheets_service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges,
            valueRenderOption=value_render_option,
            dateTimeRenderOption=date_time_render_option
        ).execute()
        
        value_ranges = result.get('valueRanges', [])
        results = []
        
        for i, value_range in enumerate(value_ranges):
            range_str = value_range.get('range', ranges[i] if i < len(ranges) else 'Unknown')
            values = value_range.get('values', [])
            row_count = len(values)
            column_count = max(len(row) for row in values) if values else 0
            
            results.append({
                "range": range_str,
                "values": values,
                "row_count": row_count,
                "column_count": column_count
            })
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "ranges": results,
            "total_ranges": len(results),
            "message": f"Successfully read {len(results)} ranges"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error reading multiple ranges: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error reading multiple ranges: {error}")

def get_sheet_metadata(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get metadata about a sheet including dimensions and properties.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Optional sheet name to get specific sheet metadata
    
    Returns:
        Dict containing sheet metadata
    """
    
    try:
        # Get spreadsheet metadata
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.data.rowData"
        ).execute()
        
        sheets = result.get('sheets', [])
        metadata = {
            "spreadsheet_id": spreadsheet_id,
            "total_sheets": len(sheets),
            "sheets": []
        }
        
        for sheet in sheets:
            props = sheet.get('properties', {})
            sheet_info = {
                "sheet_id": props.get('sheetId'),
                "title": props.get('title'),
                "index": props.get('index'),
                "grid_properties": props.get('gridProperties', {}),
                "hidden": props.get('hidden', False),
                "tab_color": props.get('tabColor', {})
            }
            
            # If specific sheet requested, return only that sheet
            if sheet_name and props.get('title') == sheet_name:
                return {
                    "spreadsheet_id": spreadsheet_id,
                    "sheet": sheet_info
                }
            
            metadata["sheets"].append(sheet_info)
        
        return metadata
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error getting sheet metadata: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error getting sheet metadata: {error}")
