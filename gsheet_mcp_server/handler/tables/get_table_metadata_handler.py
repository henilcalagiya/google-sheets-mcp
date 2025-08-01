"""Handler for getting table metadata from Google Sheets."""

from typing import Dict, Any, Optional
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names, get_table_info
from gsheet_mcp_server.helper.json_utils import compact_json_response


def get_table_metadata_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str
) -> str:
    """
    Get comprehensive metadata for a specific table in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to get metadata for
    
    Returns:
        str: JSON-formatted string containing table metadata or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required and cannot be empty."
            })
        
        # Get spreadsheet ID using utility function
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })

        # Get sheet ID using utility function
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
            })
        
        # Get table ID
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [table_name])
        table_id = table_ids.get(table_name)
        if not table_id:
            return compact_json_response({
                "success": False,
                "message": f"Table '{table_name}' not found in sheet '{sheet_name}'."
            })
        
        # Get comprehensive table metadata using the existing utility function
        try:
            table_metadata = get_table_info(sheets_service, spreadsheet_id, table_id)
            
            # Format the response for better readability
            formatted_metadata = {
                "table_name": table_metadata.get("table_name"),
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "dimensions": {
                    "column_count": table_metadata.get("column_count"),
                    "row_count": table_metadata.get("row_count")
                },
                "range": {
                    "start_row": table_metadata.get("start_row"),
                    "end_row": table_metadata.get("end_row"),
                    "start_column": table_metadata.get("start_col"),
                    "end_column": table_metadata.get("end_col")
                },
                "range_notation": f"A{table_metadata.get('start_row', 0) + 1}:{_get_column_letter(table_metadata.get('end_col', 0) - 1)}{table_metadata.get('end_row', 0)}",
                "columns": table_metadata.get("columns", [])
            }
            
            return compact_json_response({
                "success": True,
                "message": f"Successfully retrieved metadata for table '{table_name}'",
                "data": formatted_metadata
            })
            
        except RuntimeError as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve metadata for table '{table_name}': {str(e)}"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error getting table metadata: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        })


def _get_column_letter(column_index: int) -> str:
    """Convert column index to letter (e.g., 0 -> A, 25 -> Z, 26 -> AA)."""
    result = ""
    while column_index >= 0:
        column_index, remainder = divmod(column_index, 26)
        result = chr(65 + remainder) + result
        column_index -= 1
    return result 