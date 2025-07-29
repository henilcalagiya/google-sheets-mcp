"""
Handler for deleting native Google Sheets tables using DeleteTableRequest.

This module provides functionality to remove existing table objects from Google Sheets.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names


class DeleteTableRequest(BaseModel):
    """Request model for deleting native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to delete")


def delete_table(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str
) -> Dict[str, Any]:
    """
    Delete a native Google Sheets table using DeleteTableRequest.
    
    This tool completely removes the table object and all its data from the sheet.
    The table structure, formatting, validation rules, and data will be permanently deleted.
    
    ⚠️ WARNING: This action is irreversible. All table data will be lost.
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete
    
    Returns:
        Dict containing deletion results with table information
        
    Raises:
        RuntimeError: If table deletion fails
    """
    try:
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            raise RuntimeError(f"Spreadsheet '{spreadsheet_name}' not found")
        
        # Get sheet ID
        sheet_id = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])[sheet_name]
        if sheet_id is None:
            raise RuntimeError(f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'")
        
        # Get table ID from table name
        table_id = get_table_id_by_name(sheets_service, spreadsheet_id, sheet_name, table_name)
        if table_id is None:
            raise RuntimeError(f"Table '{table_name}' not found in sheet '{sheet_name}'")
        
        # Create delete request for table
        request_body = {
            "requests": [
                {
                    "deleteTable": {
                        "tableId": table_id
                    }
                }
            ]
        }
        
        # Execute the request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        # Check if deletion was successful
        if 'replies' in response and response['replies']:
            deleted_table = response['replies'][0].get('deleteTable', {}).get('table', {})
            
            return {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "table_id": table_id,
                "message": f"Successfully deleted table '{table_name}' from sheet '{sheet_name}'"
            }
        else:
            raise RuntimeError("No response received from table deletion request")
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error deleting table: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error deleting table: {error}")


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