"""
Handler for getting metadata about native Google Sheets tables.

This module provides functionality to retrieve comprehensive metadata about table objects.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name
from ..helper.sheets_utils import get_sheet_ids_by_names
from ..helper.tables_utils import get_table_info, get_table_ids_by_names
from ..helper.json_utils import compact_json_response


class GetTableMetadataRequest(BaseModel):
    """Request model for getting metadata about native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to get metadata for")


def get_table_metadata(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str
) -> str:
    """
    Get comprehensive metadata about a native Google Sheets table.
    
    This tool retrieves detailed information about a table including:
    - Table properties (name, range, column/row counts)
    - Column properties (types, formatting, validation)
    - Row properties and formatting
    - Table styling and appearance
    - Data validation rules
    - Table filters and sorting
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to get metadata for
    
    Returns:
        Compact JSON string containing comprehensive table metadata
        
    Raises:
        RuntimeError: If table metadata retrieval fails
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
        
        # Get table ID
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [table_name])
        table_id = table_ids.get(table_name)
        if not table_id:
            return compact_json_response({
                "success": False,
                "message": f"Table '{table_name}' not found in sheet '{sheet_name}'"
            })
        
        # Get comprehensive table metadata using centralized function
        try:
            table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
            
            # Return the processed table metadata
            return compact_json_response({
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "table_id": table_id,
                "table_metadata": table_info,
                "message": f"Successfully retrieved metadata for table '{table_name}'"
            })
            
        except RuntimeError as error:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve table information: {str(error)}"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error getting table metadata: {str(error)}"
        }) 