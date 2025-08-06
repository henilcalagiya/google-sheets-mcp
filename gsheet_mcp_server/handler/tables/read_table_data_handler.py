"""Handler for reading table data by row in Google Sheets."""

from typing import Dict, List, Union, Optional
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def read_table_data_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    start_row: Optional[int] = None,
    end_row: Optional[int] = None,
    include_headers: bool = True,
    max_rows: Optional[int] = None
) -> str:
    """
    Read table data by row using the spreadsheets.tables.get API.
    
    This handler retrieves table data row by row with optional filtering and pagination.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to read data from
        start_row: Starting row index (0-based, optional)
        end_row: Ending row index (0-based, optional)
        include_headers: Whether to include header row in results
        max_rows: Maximum number of rows to return (optional)
    
    Returns:
        str: Success message with table data or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        # Validate row indices
        if start_row is not None and start_row < 0:
            return compact_json_response({
                "success": False,
                "message": "start_row must be non-negative."
            })
        
        if end_row is not None and end_row < 0:
            return compact_json_response({
                "success": False,
                "message": "end_row must be non-negative."
            })
        
        if start_row is not None and end_row is not None and start_row >= end_row:
            return compact_json_response({
                "success": False,
                "message": "start_row must be less than end_row."
            })
        
        if max_rows is not None and max_rows <= 0:
            return compact_json_response({
                "success": False,
                "message": "max_rows must be positive."
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
        
        # Get table data using spreadsheets.tables.get
        try:
            table_response = sheets_service.spreadsheets().tables().get(
                spreadsheetId=spreadsheet_id,
                tableId=table_id
            ).execute()
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve table data: {str(e)}"
            })
        
        # Extract table information
        table_data = table_response.get('rows', [])
        table_info = table_response.get('table', {})
        columns = table_info.get('columns', [])
        
        # Get column names
        column_names = [col.get('name', f'Column {i}') for i, col in enumerate(columns)]
        
        # Process rows based on parameters
        processed_rows = []
        total_rows = len(table_data)
        
        # Determine row range
        actual_start_row = start_row if start_row is not None else 0
        actual_end_row = end_row if end_row is not None else total_rows
        
        # Validate row range
        if actual_start_row >= total_rows:
            return compact_json_response({
                "success": False,
                "message": f"start_row ({actual_start_row}) is beyond table size ({total_rows})."
            })
        
        if actual_end_row > total_rows:
            actual_end_row = total_rows
        
        # Extract rows within range
        rows_in_range = table_data[actual_start_row:actual_end_row]
        
        # Apply max_rows limit if specified
        if max_rows is not None and len(rows_in_range) > max_rows:
            rows_in_range = rows_in_range[:max_rows]
        
        # Process each row
        for i, row in enumerate(rows_in_range):
            row_index = actual_start_row + i
            row_data = row.get('values', [])
            
            # Create row object
            processed_row = {
                "row_index": row_index,
                "data": row_data
            }
            
            # Add column mapping if headers are included
            if include_headers and len(column_names) == len(row_data):
                processed_row["column_data"] = dict(zip(column_names, row_data))
            
            processed_rows.append(processed_row)
        
        # Prepare response data
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_info": {
                "total_rows": total_rows,
                "total_columns": len(column_names),
                "column_names": column_names,
                "start_row": actual_start_row,
                "end_row": actual_end_row,
                "rows_returned": len(processed_rows)
            },
            "rows": processed_rows,
            "message": f"Successfully retrieved {len(processed_rows)} row(s) from table '{table_name}'"
        }
        
        return compact_json_response(response_data)
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error reading table data: {str(e)}"
        }) 