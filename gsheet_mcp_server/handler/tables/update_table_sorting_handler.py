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

def update_table_sorting_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_name: str,
    sort_order: str = "ASC"
) -> str:
    """
    Apply basic filter sorting to a table in Google Sheets and then remove the filter.
    
    This function uses the setBasicFilter request to sort table data using the filter functionality,
    then removes the filter to allow new records to be added.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to sort
        column_name: Name of the column to sort by
        sort_order: Sort order ("ASC" or "DESC")
    
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
        
        if not column_name or column_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Column name is required."
            })
        
        # Validate sort order
        valid_orders = ["ASC", "DESC"]
        if sort_order not in valid_orders:
            return compact_json_response({
                "success": False,
                "message": f"Invalid sort order: {sort_order}. Valid orders are: {', '.join(valid_orders)}"
            })
        
        # Convert short names to Google Sheets API values
        api_sort_order = "ASCENDING" if sort_order == "ASC" else "DESCENDING"
        
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
        
        # Validate sort column exists in table
        if column_name not in column_names:
            return compact_json_response({
                "success": False,
                "message": f"Sort column '{column_name}' not found in table. Available columns: {', '.join(column_names)}"
            })
        
        # Find column index
        col_index = column_names.index(column_name)
        
        # Create setBasicFilter request according to official API documentation
        # This applies sorting using the filter functionality
        set_basic_filter_request = {
            "setBasicFilter": {
                "filter": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_start_row,
                        "endRowIndex": table_end_row,
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": table_end_col
                    },
                    "sortSpecs": [
                        {
                            "dimensionIndex": col_index,
                            "sortOrder": api_sort_order
                        }
                    ]
                }
            }
        }
        
        # Create clearBasicFilter request to remove the filter after sorting
        clear_basic_filter_request = {
            "clearBasicFilter": {
                "sheetId": sheet_id
            }
        }
        
        # Execute both requests: first sort, then remove filter
        try:
            response = sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [set_basic_filter_request, clear_basic_filter_request]}
            ).execute()
        except Exception as api_error:
            return compact_json_response({
                "success": False,
                "message": f"API call failed: {str(api_error)}"
            })
        
        # Extract response information
        replies = response.get("replies", [])
        
        # Debug: Log the response structure
        print(f"Debug - Response keys: {list(response.keys())}")
        print(f"Debug - Replies: {replies}")
        
        # Check if the request was successful (any reply means success)
        if replies and len(replies) > 0:
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "table_id": table_id,
                "sort_column": column_name,
                "sort_order": sort_order,
                "rows_sorted": table_end_row - table_start_row,
                "filter_removed": True,
                "message": f"Successfully sorted table '{table_name}' by '{column_name}' ({sort_order}) and removed filter in '{sheet_name}'"
            }
            
            return compact_json_response(response_data)
        else:
            return compact_json_response({
                "success": False,
                "message": "Failed to apply sorting and remove filter - no response data from API"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error applying sorting and removing filter: {str(e)}"
        }) 