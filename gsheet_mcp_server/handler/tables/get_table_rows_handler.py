"""Handler for retrieving table rows from Google Sheets."""

from typing import List, Dict, Any, Optional
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def get_table_rows_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    start_row: int,
    end_row: int,
    include_headers: bool = False
) -> str:
    """
    Retrieve rows from a table in Google Sheets using the official values().get() operation.
    
    According to the official Google Sheets API documentation, to get table data:
    1. Use values().get() to retrieve cell values from the table range
    2. Optionally filter by row range and include/exclude headers
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to get rows from
        start_row: Starting row index (1-based, excluding header)
        end_row: Ending row index (1-based, excluding header)
        include_headers: Whether to include header row in results (default: False)
    
    Returns:
        str: Success message with table rows data or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        # Validate row indices if provided
        if start_row is not None and (not isinstance(start_row, int) or start_row < 1):
            return compact_json_response({
                "success": False,
                "message": "Start row must be a positive integer (1 or greater)."
            })
        
        if end_row is not None and (not isinstance(end_row, int) or end_row < 1):
            return compact_json_response({
                "success": False,
                "message": "End row must be a positive integer (1 or greater)."
            })
        
        if start_row is not None and end_row is not None and start_row > end_row:
            return compact_json_response({
                "success": False,
                "message": "Start row cannot be greater than end row."
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
        
        # Calculate the range to retrieve
        if include_headers:
            # Include header row
            range_start_row = table_start_row
            range_end_row = table_end_row
        else:
            # Exclude header row
            range_start_row = table_start_row + 1
            range_end_row = table_end_row
        
        # Apply user-specified row range if provided
        if start_row is not None:
            user_start_row = table_start_row + start_row
            if include_headers:
                user_start_row = table_start_row + start_row - 1
            range_start_row = max(range_start_row, user_start_row)
        
        if end_row is not None:
            user_end_row = table_start_row + end_row
            if include_headers:
                user_end_row = table_start_row + end_row
            range_end_row = min(range_end_row, user_end_row)
        
        # Check if there's data to retrieve
        if range_start_row >= range_end_row:
            return compact_json_response({
                "success": False,
                "message": "No data to retrieve. Table is empty or specified range is invalid."
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
                    "rows_retrieved": 0,
                    "data": [],
                    "message": f"No data found in table '{table_name}' for the specified range."
                })
            
            # Process the retrieved data
            processed_rows = []
            for i, row in enumerate(values):
                # Pad row with empty values if it's shorter than expected
                while len(row) < (table_end_col - table_start_col):
                    row.append("")
                
                # Truncate row if it's longer than expected
                row = row[:table_end_col - table_start_col]
                
                processed_rows.append(row)
            
            # Prepare response data
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "rows_retrieved": len(processed_rows),
                "columns_count": len(processed_rows[0]) if processed_rows else 0,
                "range_retrieved": range_a1,
                "include_headers": include_headers,
                "data": processed_rows,
                "message": f"Successfully retrieved {len(processed_rows)} row(s) from table '{table_name}' in '{sheet_name}'"
            }
            
            # Add column information if headers are included
            if include_headers and columns:
                response_data["column_info"] = [
                    {
                        "name": col.get("name", ""),
                        "type": col.get("type", "TEXT"),
                        "index": col.get("index", 0)
                    }
                    for col in columns
                ]
            
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
            "message": f"Error retrieving table rows: {str(e)}"
        }) 