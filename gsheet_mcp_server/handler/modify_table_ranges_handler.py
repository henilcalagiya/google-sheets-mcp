"""
Handler for modifying ranges within native Google Sheets tables using InsertRangeRequest/DeleteRangeRequest.

This module provides unified functionality to insert or delete ranges of cells within existing table objects.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names


class ModifyTableRangesRequest(BaseModel):
    """Request model for modifying ranges within native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to modify ranges in")
    operation: str = Field(..., description="Operation to perform: INSERT or DELETE")
    range_to_modify: str = Field(..., description="Range to modify (e.g., 'A1:C5')")
    shift_direction: str = Field(default="ROWS", description="Shift direction: ROWS or COLUMNS")
    data: Optional[List[List[str]]] = Field(default=None, description="Data to insert (for INSERT operations)")


def modify_table_ranges(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    operation: str,
    range_to_modify: str,
    shift_direction: str = "ROWS",
    data: Optional[List[List[str]]] = None
) -> Dict[str, Any]:
    """
    Modify ranges within a native Google Sheets table using InsertRangeRequest/DeleteRangeRequest.
    
    This unified tool can either insert or delete ranges of cells and shift existing data accordingly.
    It's more precise than dimension-based operations as it works with specific ranges.
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to modify ranges in
        operation: Operation to perform ("INSERT" or "DELETE")
        range_to_modify: Range to modify (e.g., 'A1:C5')
        shift_direction: Shift direction ("ROWS" or "COLUMNS")
        data: Optional data to insert (for INSERT operations)
    
    Returns:
        Dict containing operation results with table information
        
    Raises:
        RuntimeError: If range modification fails
    """
    try:
        # Validate operation
        if operation not in ["INSERT", "DELETE"]:
            raise RuntimeError("Operation must be 'INSERT' or 'DELETE'")
        
        # Validate shift direction
        if shift_direction not in ["ROWS", "COLUMNS"]:
            raise RuntimeError("Shift direction must be 'ROWS' or 'COLUMNS'")
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            raise RuntimeError(f"Spreadsheet '{spreadsheet_name}' not found")
        
        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            raise RuntimeError(f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'")
        
        # Get table ID and info
        table_id = get_table_id_by_name(sheets_service, spreadsheet_id, sheet_name, table_name)
        if not table_id:
            raise RuntimeError(f"Table '{table_name}' not found in sheet '{sheet_name}'")
        
        # Get table info for validation
        table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        if not table_info:
            raise RuntimeError(f"Could not retrieve table information for '{table_name}'")
        
        # Parse range to get start and end coordinates
        start_row, start_col, end_row, end_col = parse_range(range_to_modify)
        
        # Validate range is within reasonable bounds
        if start_row < 0 or start_col < 0 or end_row < 0 or end_col < 0:
            raise RuntimeError(f"Invalid range coordinates: start_row={start_row}, start_col={start_col}, end_row={end_row}, end_col={end_col}")
        
        if start_row >= end_row or start_col >= end_col:
            raise RuntimeError(f"Invalid range: start must be before end. Got: {range_to_modify}")
        
        print(f"DEBUG: Parsed range '{range_to_modify}' -> start_row={start_row}, start_col={start_col}, end_row={end_row}, end_col={end_col}")
        print(f"DEBUG: Table info: {table_info}")
        
        # Create request based on operation
        if operation == "INSERT":
            request_body = {
                "requests": [
                    {
                        "insertRange": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": start_row,
                                "endRowIndex": end_row,
                                "startColumnIndex": start_col,
                                "endColumnIndex": end_col
                            },
                            "shiftDimension": shift_direction
                        }
                    }
                ]
            }
        else:  # DELETE
            request_body = {
                "requests": [
                    {
                        "deleteRange": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": start_row,
                                "endRowIndex": end_row,
                                "startColumnIndex": start_col,
                                "endColumnIndex": end_col
                            },
                            "shiftDimension": shift_direction
                        }
                    }
                ]
            }
        
        # Execute the request
        print(f"DEBUG: Executing {operation} request with body: {request_body}")
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        print(f"DEBUG: API Response: {response}")
        
        # If data is provided for INSERT operation, write it to the inserted range
        if operation == "INSERT" and data:
            range_name = f"{sheet_name}!{range_to_modify}"
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body={"values": data}
            ).execute()
        
        # Get updated table information
        updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        
        operation_text = "inserted" if operation == "INSERT" else "deleted"
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": table_id,
            "operation": operation,
            "range_modified": range_to_modify,
            "shift_direction": shift_direction,
            "data_inserted": bool(data) if operation == "INSERT" else False,
            "updated_table_info": updated_table_info,
            "message": f"Successfully {operation_text} range '{range_to_modify}' in table '{table_name}' with {shift_direction} shift"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        raise RuntimeError(f"Error modifying table ranges: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error modifying table ranges: {error}")


def parse_range(range_str: str) -> tuple:
    """
    Parse A1 notation range to get start and end coordinates.
    
    Args:
        range_str: Range in A1 notation (e.g., 'A1:C5')
    
    Returns:
        Tuple of (start_row, start_col, end_row, end_col) in 0-based indices
    """
    try:
        # Split range into start and end
        if ':' in range_str:
            start, end = range_str.split(':')
        else:
            start = end = range_str
        
        # Parse start coordinates
        start_col_letters = ''.join(filter(str.isalpha, start))
        start_row_num = int(''.join(filter(str.isdigit, start)))
        start_col = col_letter_to_index(start_col_letters)
        start_row = start_row_num - 1  # Convert to 0-based
        
        # Parse end coordinates
        end_col_letters = ''.join(filter(str.isalpha, end))
        end_row_num = int(''.join(filter(str.isdigit, end)))
        end_col = col_letter_to_index(end_col_letters)
        end_row = end_row_num  # Keep as 1-based for API (exclusive)
        
        return start_row, start_col, end_row, end_col
        
    except Exception as e:
        raise RuntimeError(f"Invalid range format '{range_str}': {e}")


def col_letter_to_index(col_letter: str) -> int:
    """
    Convert column letter to 0-based index.
    
    Args:
        col_letter: Column letter (e.g., 'A', 'B', 'AA')
    
    Returns:
        0-based column index
    """
    index = 0
    for char in col_letter:
        index = index * 26 + (ord(char.upper()) - ord('A') + 1)
    return index - 1


def get_table_id_by_name(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str,
    table_name: str
) -> str:
    """
    Get table ID from table name.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet
        table_name: Name of the table
    
    Returns:
        Table ID if found, None otherwise
    """
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        # Search for the table in the specified sheet
        for sheet in result.get("sheets", []):
            if sheet.get("properties", {}).get("title") == sheet_name:
                tables = sheet.get("tables", [])
                for table in tables:
                    if table.get("name") == table_name:
                        return table.get("tableId")
                break
        
        return None
        
    except Exception as e:
        raise RuntimeError(f"Error getting table ID: {e}")


def get_table_info(
    sheets_service,
    spreadsheet_id: str,
    table_id: str
) -> Dict[str, Any]:
    """
    Get detailed information about a table.
    
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
        
        # Search for the table
        for sheet in result.get("sheets", []):
            tables = sheet.get("tables", [])
            for table in tables:
                if table.get("tableId") == table_id:
                    return {
                        "table_id": table.get("tableId"),
                        "name": table.get("name"),
                        "range": table.get("range", {}),
                        "row_count": table.get("rowCount", 0),
                        "column_count": table.get("columnCount", 0)
                    }
        
        return {}
        
    except Exception as e:
        raise RuntimeError(f"Error getting table info: {e}") 