"""Handler for getting cell values by range from sheets in Google Sheets."""

from typing import List, Dict, Any, Optional, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import parse_cell_reference
from gsheet_mcp_server.helper.json_utils import compact_json_response

def get_sheet_cells_by_range_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str,
    include_headers: bool = False
) -> str:
    """
    Get values from a range of cells in a sheet in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to get cells from
        start_cell: Starting cell reference (e.g., 'A1', 'B2')
        end_cell: Ending cell reference (e.g., 'C5', 'D10')
        include_headers: Whether to include header row in results
    
    Returns:
        str: Success message with cell values and mapping or error message
    """
    try:
        # Validate inputs
        if not start_cell or not isinstance(start_cell, str):
            return compact_json_response({
                "success": False,
                "message": "Start cell is required and must be a string."
            })
        
        if not end_cell or not isinstance(end_cell, str):
            return compact_json_response({
                "success": False,
                "message": "End cell is required and must be a string."
            })
        
        # Validate cell references
        try:
            start_row, start_col = parse_cell_reference(start_cell.strip())
            end_row, end_col = parse_cell_reference(end_cell.strip())
        except ValueError as e:
            return compact_json_response({
                "success": False,
                "message": f"Invalid cell reference format: {str(e)}"
            })
        
        # Validate range (start should be before end)
        if start_row > end_row or (start_row == end_row and start_col > end_col):
            return compact_json_response({
                "success": False,
                "message": "Start cell must be before or equal to end cell in the range."
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

        # Get cell values using sheets.values.get
        try:
            # Create range notation
            range_notation = f"'{sheet_name}'!{start_cell.strip()}:{end_cell.strip()}"
            
            response = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_notation
            ).execute()
            
            values = response.get('values', [])
            
            if not values:
                return compact_json_response({
                    "success": True,
                    "message": f"No data found in range {start_cell}:{end_cell}",
                    "spreadsheet_name": spreadsheet_name,
                    "sheet_name": sheet_name,
                    "range": f"{start_cell}:{end_cell}",
                    "cell_count": 0,
                    "data": [],
                    "summary": {
                        "total_rows": 0,
                        "total_columns": 0,
                        "non_empty_cells": 0
                    }
                })
            
            # Process the data
            processed_data = []
            non_empty_cells = 0
            
            for row_idx, row in enumerate(values):
                processed_row = []
                for col_idx, cell_value in enumerate(row):
                    if cell_value is not None and str(cell_value).strip() != "":
                        non_empty_cells += 1
                    processed_row.append(cell_value)
                processed_data.append(processed_row)
            
            # Calculate dimensions
            max_cols = max(len(row) for row in processed_data) if processed_data else 0
            total_rows = len(processed_data)
            
            # Prepare response
            response_data = {
                "success": True,
                "message": f"Successfully retrieved data from range {start_cell}:{end_cell}",
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "range": f"{start_cell}:{end_cell}",
                "cell_count": total_rows * max_cols if total_rows > 0 and max_cols > 0 else 0,
                "data": processed_data,
                "summary": {
                    "total_rows": total_rows,
                    "total_columns": max_cols,
                    "non_empty_cells": non_empty_cells,
                    "empty_cells": (total_rows * max_cols) - non_empty_cells if total_rows > 0 and max_cols > 0 else 0
                }
            }
            
            return compact_json_response(response_data)
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            return compact_json_response({
                "success": False,
                "message": f"Failed to retrieve cell values: {error_details}",
                "error_code": e.resp.status if hasattr(e, 'resp') else None
            })
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        })
