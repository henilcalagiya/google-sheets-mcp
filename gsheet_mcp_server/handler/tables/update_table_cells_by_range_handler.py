"""Handler for updating table cells by range in Google Sheets."""

from typing import List, Dict, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    validate_cell_value,
    parse_cell_reference,
    column_index_to_letter
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_table_cells_by_range_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    start_cell: str,
    end_cell: str,
    cell_values: List[List[Union[str, int, float, bool, None]]]
) -> str:
    """
    Update table cells by range in Google Sheets using the official updateCells operation.
    
    According to the official Google Sheets API documentation, to update cells by range:
    1. Use UpdateCellsRequest to update cells in the specified range
    2. Apply proper formatting based on column types
    3. Validate cell values before updating
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        start_cell: Starting cell reference (e.g., 'A1', 'B2')
        end_cell: Ending cell reference (e.g., 'C5', 'D10')
        cell_values: 2D array of values to update (rows x columns)
    
    Returns:
        str: Success message with update details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if not start_cell or not end_cell:
            return compact_json_response({
                "success": False,
                "message": "Both start_cell and end_cell are required."
            })
        
        if not cell_values or not isinstance(cell_values, list):
            return compact_json_response({
                "success": False,
                "message": "Cell values are required and must be a 2D array."
            })
        
        # Parse cell references
        try:
            start_row, start_col = parse_cell_reference(start_cell)
            end_row, end_col = parse_cell_reference(end_cell)
        except ValueError as e:
            return compact_json_response({
                "success": False,
                "message": f"Invalid cell reference: {str(e)}"
            })
        
        # Validate range
        if start_row > end_row or start_col > end_col:
            return compact_json_response({
                "success": False,
                "message": "Invalid range. start_cell should be top-left and end_cell should be bottom-right."
            })
        
        expected_rows = end_row - start_row + 1
        expected_cols = end_col - start_col + 1
        
        if len(cell_values) != expected_rows:
            return compact_json_response({
                "success": False,
                "message": f"Expected {expected_rows} rows, but got {len(cell_values)} rows."
            })
        
        # Validate cell values structure
        validated_values = []
        invalid_cells = []
        
        for row_idx, row in enumerate(cell_values):
            if not isinstance(row, list):
                invalid_cells.append({"row": start_row + row_idx + 1, "error": "Row must be a list"})
                continue
            
            if len(row) != expected_cols:
                invalid_cells.append({
                    "row": start_row + row_idx + 1, 
                    "error": f"Expected {expected_cols} columns, but got {len(row)} columns"
                })
                continue
            
            validated_row = []
            for col_idx, value in enumerate(row):
                # Validate cell value
                value_validation = validate_cell_value(value)
                if not value_validation["valid"]:
                    invalid_cells.append({
                        "row": start_row + row_idx + 1,
                        "column": start_col + col_idx + 1,
                        "error": value_validation["error"]
                    })
                    continue
                
                validated_row.append(value_validation["cleaned_value"])
            
            validated_values.append(validated_row)
        
        if invalid_cells:
            error_messages = [f"Row {item['row']}, Col {item.get('column', 'N/A')}: {item['error']}" for item in invalid_cells]
            return compact_json_response({
                "success": False,
                "message": f"Invalid cell values: {'; '.join(error_messages)}",
                "invalid_cells": invalid_cells
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
                "message": f"Failed to get table information: {str(e)}"
            })
        
        if not table_range:
            return compact_json_response({
                "success": False,
                "message": f"Table '{table_name}' has no valid range."
            })
        
        # Convert table coordinates to sheet coordinates
        table_start_row = table_range.get('startRowIndex', 0)
        table_start_col = table_range.get('startColumnIndex', 0)
        
        # Calculate sheet coordinates (end indices are exclusive)
        sheet_start_row = table_start_row + start_row
        sheet_end_row = table_start_row + end_row + 1  # Add 1 for exclusive
        sheet_start_col = table_start_col + start_col
        sheet_end_col = table_start_col + end_col + 1  # Add 1 for exclusive
        
        # Convert to A1 notation
        start_cell_sheet = f"{column_index_to_letter(sheet_start_col)}{sheet_start_row + 1}"
        end_cell_sheet = f"{column_index_to_letter(sheet_end_col)}{sheet_end_row + 1}"
        range_notation = f"{sheet_name}!{start_cell_sheet}:{end_cell_sheet}"
        
        # Update cell values
        try:
            body = {
                'values': validated_values
            }
            
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_notation,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            
            return compact_json_response({
                "success": True,
                "message": f"Successfully updated {updated_cells} cells in table '{table_name}'",
                "data": {
                    "table_name": table_name,
                    "range": {
                        "start_cell": start_cell,
                        "end_cell": end_cell,
                        "start_row": start_row + 1,  # Convert back to 1-based
                        "end_row": end_row + 1,
                        "start_column": start_col + 1,  # Convert back to 1-based
                        "end_column": end_col + 1
                    },
                    "updated_cells": updated_cells,
                    "updated_range": result.get('updatedRange', range_notation)
                }
            })
            
        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            return compact_json_response({
                "success": False,
                "message": f"Failed to update cell data: {error_details.get('message', str(e))}",
                "error_code": e.resp.status
            })
            
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        })
