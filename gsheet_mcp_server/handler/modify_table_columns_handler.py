"""
Handler for inserting and deleting columns within native Google Sheets tables using InsertDimensionRequest/DeleteDimensionRequest.

This module provides functionality to insert or delete columns within existing table objects.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names


class TableColumnsRequest(BaseModel):
    """Request model for inserting/deleting columns within native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to modify columns in")
    operation: str = Field(..., description="Operation to perform: INSERT or DELETE")
    position: int = Field(..., description="Position where to insert/delete columns (0-based)")
    count: int = Field(..., description="Number of columns to insert/delete")


def modify_table_columns(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    operation: str,
    position: int,
    count: int
) -> Dict[str, Any]:
    """
    Insert or delete columns within a native Google Sheets table using InsertDimensionRequest/DeleteDimensionRequest.
    
    This tool can either insert empty columns (shifting existing data right) or delete columns (shifting existing data left).
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to modify columns in
        operation: Operation to perform ("INSERT" or "DELETE")
        position: Position where to insert/delete columns (0-based)
        count: Number of columns to insert/delete
    
    Returns:
        Dict containing operation results with table information
        
    Raises:
        RuntimeError: If column operation fails
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
        
        # Get table ID
        table_id = get_table_id_by_name(sheets_service, spreadsheet_id, sheet_name, table_name)
        if not table_id:
            raise RuntimeError(f"Table '{table_name}' not found in sheet '{sheet_name}'")
        
        # Validate parameters
        if position < 0:
            raise RuntimeError("Position must be >= 0")
        if count <= 0:
            raise RuntimeError("Count must be > 0")
        
        # Validate operation
        if operation not in ["INSERT", "DELETE"]:
            raise RuntimeError("Operation must be 'INSERT' or 'DELETE'")
        
        # Calculate start and end indices
        start_index = position
        end_index = position + count
        
        # Create the request based on operation
        if operation == "INSERT":
            request_body = {
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": start_index,
                                "endIndex": end_index
                            },
                            "inheritFromBefore": True
                        }
                    }
                ]
            }
        else:  # DELETE
            request_body = {
                "requests": [
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": start_index,
                                "endIndex": end_index
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
        
        # Get updated table information
        updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        
        operation_text = "inserted" if operation == "INSERT" else "deleted"
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "operation": operation,
            "dimension": "COLUMNS",
            "position": position,
            "count": count,
            "columns_affected": count,
            "updated_table_info": updated_table_info,
            "message": f"Successfully {operation_text} {count} columns at position {position} in table '{table_name}'"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        raise RuntimeError(f"Error modifying table columns: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error modifying table columns: {error}")


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
        
    except Exception as error:
        raise RuntimeError(f"Error getting table ID: {error}")


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
                    table_range = table.get("range", {})
                    return {
                        "table_name": table.get("name", "Unknown"),
                        "range": table_range,
                        "column_count": table_range.get("endColumnIndex", 0) - table_range.get("startColumnIndex", 0),
                        "row_count": table_range.get("endRowIndex", 0) - table_range.get("startRowIndex", 0),
                        "column_properties": table.get("columnProperties", []),
                        "rows_properties": table.get("rowsProperties", [])
                    }
        
        raise RuntimeError(f"Table with ID '{table_id}' not found")
        
    except Exception as error:
        raise RuntimeError(f"Error getting table info: {error}")