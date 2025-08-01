"""Handler for modifying cell data in Google Sheets."""

from typing import List, Any, Dict, Optional
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names, get_table_info
from gsheet_mcp_server.helper.json_utils import compact_json_response


def _parse_cell_location(cell_ref: str) -> tuple[int, int]:
    """
    Parse Excel cell reference (e.g., 'A1', 'B2') to row and column indices.
    
    Args:
        cell_ref: Excel cell reference (e.g., 'A1', 'B2')
    
    Returns:
        tuple: (row_index, column_index) where both are 0-based
    """
    import re
    
    # Match pattern like 'A1', 'B2', 'AA123', etc.
    match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.upper())
    if not match:
        raise ValueError(f"Invalid cell reference: {cell_ref}")
    
    column_str, row_str = match.groups()
    
    # Convert column letters to index (A=0, B=1, AA=26, etc.)
    column_index = 0
    for char in column_str:
        column_index = column_index * 26 + (ord(char) - ord('A') + 1)
    column_index -= 1  # Make it 0-based
    
    # Convert row string to index (1-based to 0-based)
    row_index = int(row_str) - 1
    
    return row_index, column_index


def modify_cell_data_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    cell_locations: List[str] = [],
    cell_values: List[str] = []
) -> str:
    """
    Modify specific cells in a table in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to modify
        cell_locations: List of cell locations (e.g., ['A2', 'B3', 'C1'])
        cell_values: List of new values for the cells
    
    Returns:
        str: Success message with update details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required and cannot be empty."
            })
        
        if not cell_locations or len(cell_locations) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one cell location is required."
            })
        
        if not cell_values or len(cell_values) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one cell value is required."
            })
        
        if len(cell_locations) != len(cell_values):
            return compact_json_response({
                "success": False,
                "message": f"Number of cell locations ({len(cell_locations)}) must match number of cell values ({len(cell_values)})."
            })
        
        # Parse cell locations and create updates
        cell_updates = []
        for i, (location, value) in enumerate(zip(cell_locations, cell_values)):
            try:
                row, column = _parse_cell_location(location)
                cell_updates.append({
                    "row": row,
                    "column": column,
                    "value": value
                })
            except ValueError as e:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid cell location '{location}': {str(e)}"
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
            table_start_row = table_info.get('start_row', 0)
            table_start_col = table_info.get('start_col', 0)
            table_end_row = table_info.get('end_row', 0)
            table_end_col = table_info.get('end_col', 0)
            current_row_count = table_info.get('row_count', 0)
            current_column_count = table_info.get('column_count', 0)
        except RuntimeError as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Validate cell positions are within table bounds
        for i, update in enumerate(cell_updates):
            row = update["row"]
            column = update["column"]
            
            if row >= current_row_count:
                return compact_json_response({
                    "success": False,
                    "message": f"Cell update {i} row {row} is outside table bounds (0-{current_row_count-1})."
                })
            
            if column >= current_column_count:
                return compact_json_response({
                    "success": False,
                    "message": f"Cell update {i} column {column} is outside table bounds (0-{current_column_count-1})."
                })
        
        # Group updates by row for efficient batch update
        row_updates = {}
        for update in cell_updates:
            row = update["row"]
            column = update["column"]
            value = update["value"]
            
            if row not in row_updates:
                row_updates[row] = {}
            row_updates[row][column] = value
        
        # Prepare batch update requests
        requests = []
        
        for row_idx, column_updates in row_updates.items():
            # Calculate actual row position in sheet
            sheet_row_index = table_start_row + row_idx
            
            # Create individual update requests for each cell to avoid affecting other cells
            for col_idx, value in column_updates.items():
                sheet_col_index = table_start_col + col_idx
                
                update_cell_request = {
                    "updateCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": sheet_row_index,
                            "endRowIndex": sheet_row_index + 1,
                            "startColumnIndex": sheet_col_index,
                            "endColumnIndex": sheet_col_index + 1
                        },
                        "rows": [{"values": [{"userEnteredValue": {"stringValue": str(value)}}]}],
                        "fields": "userEnteredValue"
                    }
                }
                requests.append(update_cell_request)
        
        # Execute batch update
        batch_request = {"requests": requests}
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_request
        ).execute()
        
        # Prepare response message
        message = f"Successfully updated {len(cell_updates)} cell(s) in table '{table_name}' in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        
        return compact_json_response({
            "success": True,
            "message": message,
            "data": {
                "table_name": table_name,
                "sheet_name": sheet_name,
                "spreadsheet_name": spreadsheet_name,
                "updated_cells": len(cell_updates),
                "cell_locations": cell_locations,
                "cell_values": cell_values
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error modifying cell data: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }) 