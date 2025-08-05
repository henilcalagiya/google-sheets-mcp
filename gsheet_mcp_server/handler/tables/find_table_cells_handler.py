"""Handler for finding specific values in table cells in Google Sheets."""

from typing import List, Dict, Any, Optional, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def find_table_cells_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    search_value: Union[str, int, float, bool],
    search_type: str = "exact",
    case_sensitive: bool = False,
    include_headers: bool = False
) -> str:
    """
    Find specific values in table cells in Google Sheets using the official values().get() operation.
    
    According to the official Google Sheets API documentation, to find values in a table:
    1. Use values().get() to retrieve all table data
    2. Search through the retrieved data for matching values
    3. Return cell positions and values that match the search criteria
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to search in
        search_value: Value to search for
        search_type: Type of search - "exact", "contains", "starts_with", "ends_with" (default: "exact")
        case_sensitive: Whether search should be case sensitive (default: False)
        include_headers: Whether to include header row in search (default: False)
    
    Returns:
        str: Success message with found cells data or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if search_value is None:
            return compact_json_response({
                "success": False,
                "message": "Search value is required."
            })
        
        valid_search_types = ["exact", "contains", "starts_with", "ends_with"]
        if search_type not in valid_search_types:
            return compact_json_response({
                "success": False,
                "message": f"Invalid search type. Valid types: {', '.join(valid_search_types)}"
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
            table_range = table_info.get('range', {})
            columns = table_info.get('columns', [])
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Get table boundaries
        table_start_row = table_range.get("startRowIndex", 0)
        table_end_row = table_range.get("endRowIndex", 0)
        table_start_col = table_range.get("startColumnIndex", 0)
        table_end_col = table_range.get("endColumnIndex", 0)
        
        # Calculate the range to search
        if include_headers:
            # Include header row
            range_start_row = table_start_row
            range_end_row = table_end_row
        else:
            # Exclude header row
            range_start_row = table_start_row + 1
            range_end_row = table_end_row
        
        # Check if there's data to search
        if range_start_row >= range_end_row:
            return compact_json_response({
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "search_value": search_value,
                "search_type": search_type,
                "matches_found": 0,
                "matches": [],
                "message": f"No data to search in table '{table_name}'."
            })
        
        # Convert to A1 notation for values().get()
        start_col_letter = chr(ord('A') + table_start_col)
        end_col_letter = chr(ord('A') + table_end_col - 1)
        start_row_number = range_start_row + 1  # Convert to 1-based
        end_row_number = range_end_row
        
        range_a1 = f"{sheet_name}!{start_col_letter}{start_row_number}:{end_col_letter}{end_row_number}"
        
        # Retrieve table data using values().get()
        try:
            response = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_a1
            ).execute()
            
            values = response.get('values', [])
            
            if not values:
                return compact_json_response({
                    "success": True,
                    "spreadsheet_name": spreadsheet_name,
                    "sheet_name": sheet_name,
                    "table_name": table_name,
                    "search_value": search_value,
                    "search_type": search_type,
                    "matches_found": 0,
                    "matches": [],
                    "message": f"No data found in table '{table_name}' to search."
                })
            
            # Search through the data
            matches = []
            search_value_str = str(search_value)
            
            for row_idx, row in enumerate(values):
                for col_idx, cell_value in enumerate(row):
                    cell_value_str = str(cell_value) if cell_value is not None else ""
                    
                    # Apply search logic based on search type
                    match_found = False
                    
                    if search_type == "exact":
                        if not case_sensitive:
                            match_found = cell_value_str.lower() == search_value_str.lower()
                        else:
                            match_found = cell_value_str == search_value_str
                    
                    elif search_type == "contains":
                        if not case_sensitive:
                            match_found = search_value_str.lower() in cell_value_str.lower()
                        else:
                            match_found = search_value_str in cell_value_str
                    
                    elif search_type == "starts_with":
                        if not case_sensitive:
                            match_found = cell_value_str.lower().startswith(search_value_str.lower())
                        else:
                            match_found = cell_value_str.startswith(search_value_str)
                    
                    elif search_type == "ends_with":
                        if not case_sensitive:
                            match_found = cell_value_str.lower().endswith(search_value_str.lower())
                        else:
                            match_found = cell_value_str.endswith(search_value_str)
                    
                    if match_found:
                        # Calculate user-friendly row and column indices
                        user_row_index = row_idx + 1 if not include_headers else row_idx
                        user_col_index = col_idx + 1
                        
                        # Get column information if available
                        column_info = None
                        if col_idx < len(columns):
                            column_info = {
                                "name": columns[col_idx].get("name", ""),
                                "type": columns[col_idx].get("type", "TEXT")
                            }
                        
                        matches.append({
                            "row_index": user_row_index,
                            "column_index": user_col_index,
                            "cell_value": cell_value,
                            "column_info": column_info
                        })
            
            # Prepare response data
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "search_value": search_value,
                "search_type": search_type,
                "case_sensitive": case_sensitive,
                "include_headers": include_headers,
                "matches_found": len(matches),
                "matches": matches,
                "message": f"Found {len(matches)} match(es) for '{search_value}' in table '{table_name}' using {search_type} search"
            }
            
            return compact_json_response(response_data)
            
        except HttpError as error:
            return compact_json_response({
                "success": False,
                "message": f"Failed to retrieve table data: {str(error)}"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error finding table cells: {str(e)}"
        }) 