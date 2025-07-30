"""
Handler for creating native Google Sheets tables using AddTableRequest.

This module provides functionality to create new table objects in Google Sheets.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names
from ..helper.json_utils import compact_json_response


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
) -> str:
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
        Compact JSON string containing table creation results
        
    Raises:
        RuntimeError: If table creation fails
    """
    try:
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found"
            })
        
        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'"
            })
        
        # Parse the table range to get start and end positions
        # Expected format: 'A1:C10' or similar
        import re
        range_match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', table_range)
        if not range_match:
            return compact_json_response({
                "success": False,
                "message": f"Invalid table range format: {table_range}. Expected format: 'A1:C10'"
            })
        
        start_col_letter, start_row_str, end_col_letter, end_row_str = range_match.groups()
        
        # Convert column letters to indices (A=0, B=1, etc.)
        def col_letter_to_index(col_letter):
            index = 0
            for char in col_letter:
                index = index * 26 + (ord(char.upper()) - ord('A') + 1)
            return index - 1
        
        start_col_index = col_letter_to_index(start_col_letter)
        # Use the number of headers to determine the end column index
        # This ensures all columns are included regardless of the range specification
        end_col_index = start_col_index + len(headers)
        start_row_index = int(start_row_str) - 1  # Convert to 0-based
        end_row_index = int(end_row_str)  # Keep as exclusive
        
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
        table_request = {
            "name": table_name,
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": start_row_index,
                "endRowIndex": start_row_index + len(table_data),
                "startColumnIndex": start_col_index,
                "endColumnIndex": end_col_index
            }
        }
        
        request_body = {
            "requests": [
                {
                    "addTable": {
                        "table": table_request
                    }
                }
            ]
        }
        
        # Execute the table creation request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        # Extract table information from response
        if 'replies' in response and response['replies']:
            table_info = response['replies'][0].get('addTable', {}).get('table', {})
            table_id = table_info.get('tableId')
            
            # Apply data validation if column_types are provided
            if column_types and len(column_types) == len(headers):
                validation_requests = []
                for i, col_type in enumerate(column_types):
                    # Only apply validation for specific types that we know work
                    if col_type.upper() in ["NUMBER", "DOUBLE", "INTEGER", "CURRENCY"]:
                        # Create data validation request for numeric columns
                        validation_request = {
                            "setDataValidation": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": start_row_index + 1,  # Skip header row
                                    "endRowIndex": start_row_index + len(table_data),
                                    "startColumnIndex": start_col_index + i,
                                    "endColumnIndex": start_col_index + i + 1
                                },
                                "rule": {
                                    "condition": {
                                        "type": "NUMBER_GREATER_THAN",
                                        "values": [{"userEnteredValue": "0"}]
                                    },
                                    "showCustomUi": True,
                                    "strict": False
                                }
                            }
                        }
                        validation_requests.append(validation_request)
                    elif col_type.upper() == "DATE":
                        # Create data validation request for date columns
                        validation_request = {
                            "setDataValidation": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": start_row_index + 1,  # Skip header row
                                    "endRowIndex": start_row_index + len(table_data),
                                    "startColumnIndex": start_col_index + i,
                                    "endColumnIndex": start_col_index + i + 1
                                },
                                "rule": {
                                    "condition": {
                                        "type": "DATE_AFTER",
                                        "values": [{"userEnteredValue": "1/1/1900"}]
                                    },
                                    "showCustomUi": True,
                                    "strict": False
                                }
                            }
                        }
                        validation_requests.append(validation_request)
                
                # Apply data validation if we have any
                if validation_requests:
                    validation_body = {"requests": validation_requests}
                    sheets_service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=validation_body
                    ).execute()
            
            return compact_json_response({
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "table_id": table_id,
                "range": table_range,
                "headers": headers,
                "data_rows": len(data) if data else 0,
                "column_count": len(headers),
                "column_types": column_types if column_types else None,
                "message": f"Successfully created table '{table_name}' with {len(data) if data else 0} rows and {len(headers)} columns (range: {start_col_letter}{start_row_str}:{chr(ord('A') + start_col_index + len(headers) - 1)}{end_row_str})"
            })
        else:
            return compact_json_response({
                "success": False,
                "message": "No response received from table creation request"
            })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        return compact_json_response({
            "success": False,
            "message": f"Error creating table: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error creating table: {error}"
        })


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