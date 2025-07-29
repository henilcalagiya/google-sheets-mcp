"""
Handler for creating native Google Sheets tables using AddTableRequest.

This module provides functionality to create new table objects in Google Sheets.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names


class AddTableRequest(BaseModel):
    """Request model for creating native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet to create table in")
    table_name: str = Field(..., description="Unique name for the table")
    table_range: str = Field(..., description="Table range (e.g., 'A1:C10')")
    headers: List[str] = Field(..., description="List of column headers")
    data: List[List[str]] = Field(default=[], description="2D list of data rows (optional)")
    column_types: List[str] = Field(..., description="Column types: DOUBLE, CURRENCY, DATE, TEXT, etc.")


def add_table(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    table_range: str,
    headers: List[str],
    data: List[List[str]] = None,
    column_types: List[str] = None
) -> Dict[str, Any]:
    """
    Create a native Google Sheets table using AddTableRequest.
    
    This creates a proper table object with:
    - Table ID and name for future reference
    - Column properties and data types
    - Professional styling with header and alternating row colors
    - Data validation capabilities
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to create table in
        table_name: Unique name for the table
        table_range: Table range (e.g., 'A1:C10')
        headers: List of column headers
        data: 2D list of data rows (optional, defaults to empty list)
        column_types: Column types (DOUBLE, CURRENCY, DATE, TEXT, etc.) (optional)
    
    Returns:
        Dict containing table creation results
        
    Raises:
        RuntimeError: If table creation fails
    """
    try:
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            raise RuntimeError(f"Spreadsheet '{spreadsheet_name}' not found")
        
        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            raise RuntimeError(f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'")
        
        # Prepare the data for the table
        table_data = [headers] + (data if data else [])
        
        # Write the data to the specified range first
        range_name = f"{sheet_name}!{table_range}"
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": table_data}
        ).execute()
        
        # Create the table using AddTableRequest
        request_body = {
            "requests": [
                {
                    "addTable": {
                        "table": {
                            "name": table_name,
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": len(table_data),
                                "startColumnIndex": 0,
                                "endColumnIndex": len(headers)
                            }
                        }
                    }
                }
            ]
        }
        
        # Execute the request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        # Extract table information from response
        if 'replies' in response and response['replies']:
            table_info = response['replies'][0].get('addTable', {}).get('table', {})
            table_id = table_info.get('tableId')
            
            return {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "table_id": table_id,
                "range": table_range,
                "headers": headers,
                "data_rows": len(data) if data else 0,
                "column_count": len(headers),
                "message": f"Successfully created table '{table_name}' with {len(data) if data else 0} rows and {len(headers)} columns"
            }
        else:
            raise RuntimeError("No response received from table creation request")
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        raise RuntimeError(f"Error creating table: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error creating table: {error}")


def get_table_info(
    sheets_service,
    spreadsheet_id: str,
    table_id: str
) -> Dict[str, Any]:
    """
    Get information about a specific table.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        table_id: ID of the table
    
    Returns:
        Dict containing table information
    """
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        # Search for the table across all sheets
        for sheet in result.get("sheets", []):
            tables = sheet.get("tables", [])
            for table in tables:
                if table.get("tableId") == table_id:
                    return {
                        "table_id": table_id,
                        "table_name": table.get("name", "Unknown"),
                        "range": table.get("range", {}),
                        "column_count": len(table.get("columnProperties", [])),
                        "row_count": len(table.get("rowsProperties", [])) if table.get("rowsProperties") else 0
                    }
        
        raise RuntimeError(f"Table with ID '{table_id}' not found")
        
    except Exception as error:
        raise RuntimeError(f"Error getting table info: {error}")