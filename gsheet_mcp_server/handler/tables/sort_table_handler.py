"""Handler for sorting tables in Google Sheets."""

from typing import List, Dict, Any, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def sort_table_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    sort_columns: List[str],
    sort_orders: List[str] = []
) -> str:
    """
    Sort a table in Google Sheets using sortRange.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to sort
        sort_columns: List of column names to sort by (in order of priority)
        sort_orders: List of sort orders ("ASCENDING" or "DESCENDING") for each column
    
    Returns:
        str: Success message with sort details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if not sort_columns or len(sort_columns) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one sort column is required."
            })
        
        # Validate sort orders if provided
        if sort_orders and len(sort_orders) != len(sort_columns):
            return compact_json_response({
                "success": False,
                "message": f"Number of sort orders ({len(sort_orders)}) must match number of sort columns ({len(sort_columns)})."
            })
        
        # Validate sort orders
        valid_orders = ["ASCENDING", "DESCENDING"]
        if sort_orders:
            invalid_orders = [order for order in sort_orders if order not in valid_orders]
            if invalid_orders:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid sort orders: {', '.join(invalid_orders)}. Valid orders are: {', '.join(valid_orders)}"
                })
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })
        
        # Get sheet ID
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
        
        # Get table information
        try:
            table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve table information: {str(e)}"
            })
        
        # Get table range
        table_range = table_info.get("range", {})
        table_start_row = table_range.get("startRowIndex", 0)
        table_end_row = table_range.get("endRowIndex", 0)
        table_start_col = table_range.get("startColumnIndex", 0)
        table_end_col = table_range.get("endColumnIndex", 0)
        
        # Get table columns
        columns = table_info.get("columns", [])
        column_names = [col.get("name", "") for col in columns]
        
        # Validate sort columns exist in table
        missing_columns = []
        for col_name in sort_columns:
            if col_name not in column_names:
                missing_columns.append(col_name)
        
        if missing_columns:
            return compact_json_response({
                "success": False,
                "message": f"Sort columns not found in table: {', '.join(missing_columns)}. Available columns: {', '.join(column_names)}"
            })
        
        # Create sort specifications
        sort_specs = []
        for i, col_name in enumerate(sort_columns):
            # Find column index
            col_index = column_names.index(col_name)
            
            # Determine sort order
            sort_order = "ASCENDING"  # Default
            if i < len(sort_orders):
                sort_order = sort_orders[i]
            
            sort_spec = {
                "dimensionIndex": col_index,
                "sortOrder": sort_order
            }
            sort_specs.append(sort_spec)
        
        # Create sortRange request according to official API documentation
        # Note: We exclude the header row from sorting
        sort_range_request = {
            "sortRange": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": table_start_row + 1,  # Start after header
                    "endRowIndex": table_end_row,
                    "startColumnIndex": table_start_col,
                    "endColumnIndex": table_end_col
                },
                "sortSpecs": sort_specs
            }
        }
        
        # Execute the sortRange request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [sort_range_request]}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        if replies and "sortRange" in replies[0]:
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "sort_columns": sort_columns,
                "sort_orders": sort_orders if sort_orders else ["ASCENDING"] * len(sort_columns),
                "rows_sorted": table_end_row - table_start_row - 1,  # Exclude header
                "message": f"Successfully sorted table '{table_name}' by {', '.join(sort_columns)} in '{sheet_name}'"
            }
            
            return compact_json_response(response_data)
        else:
            return compact_json_response({
                "success": False,
                "message": "Failed to sort table - no response data from API"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error sorting table: {str(e)}"
        }) 