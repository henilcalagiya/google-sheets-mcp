"""Handler for updating individual cell values in tables in Google Sheets."""

from typing import List, Dict, Any, Optional, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    parse_cell_reference
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_table_cells_by_notation_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    cell_updates: List[Dict[str, Union[str, int, float, bool, None]]]
) -> str:
    """
    Update specific cell values in a table in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        cell_updates: List of cell updates, each containing cell_notation and value
    
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
        
        if not cell_updates or not isinstance(cell_updates, list):
            return compact_json_response({
                "success": False,
                "message": "Cell updates are required and must be a list."
            })
        
        if len(cell_updates) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one cell update is required."
            })
        
        # Validate cell updates structure
        validated_updates = []
        invalid_updates = []
        
        for i, update in enumerate(cell_updates):
            if not isinstance(update, dict):
                invalid_updates.append({"index": i, "error": "Update must be a dictionary"})
                continue
            
            cell_notation = update.get("cell_notation")
            value = update.get("value")
            
            if not isinstance(cell_notation, str) or not cell_notation.strip():
                invalid_updates.append({"index": i, "error": "cell_notation must be a valid string"})
                continue
            
            try:
                # Validate A1 notation format
                row_idx, col_idx = parse_cell_reference(cell_notation.strip())
                validated_updates.append({
                    "cell_notation": cell_notation.strip(),
                    "value": value,
                    "row_index": row_idx,
                    "column_index": col_idx
                })
            except ValueError:
                invalid_updates.append({"index": i, "error": f"Invalid A1 notation: {cell_notation}"})
        
        if invalid_updates:
            error_messages = [f"Update {item['index']+1}: {item['error']}" for item in invalid_updates]
            return compact_json_response({
                "success": False,
                "message": f"Invalid cell updates: {'; '.join(error_messages)}",
                "invalid_updates": invalid_updates
            })
        
        if not validated_updates:
            return compact_json_response({
                "success": False,
                "message": "No valid cell updates provided."
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
        
        # Update cell values
        updated_cells = []
        failed_cells = []
        total_updated = 0
        
        for update in validated_updates:
            try:
                cell_notation = update["cell_notation"]
                value = update["value"]
                
                # Convert to sheet notation
                range_notation = f"{sheet_name}!{cell_notation}"
                
                # Update cell value
                body = {
                    'values': [[value]]
                }
                
                result = sheets_service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_notation,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                cells_updated = result.get('updatedCells', 0)
                total_updated += cells_updated
                
                updated_cells.append({
                    "cell_notation": cell_notation,
                    "value": value,
                    "updated_cells": cells_updated,
                    "updated_range": result.get('updatedRange', range_notation)
                })
                
            except Exception as e:
                failed_cells.append({
                    "cell_notation": update["cell_notation"],
                    "value": update["value"],
                    "error": str(e)
                })
        
        # Prepare response data
        response_data = {
            "success": True,
            "table_name": table_name,
            "cells_requested": len(validated_updates),
            "cells_updated": len(updated_cells),
            "total_cells_updated": total_updated,
            "updated_cells": updated_cells,
            "message": f"Successfully updated {len(updated_cells)} cell(s) in table '{table_name}'"
        }
        
        if failed_cells:
            response_data["failed_cells"] = failed_cells
            response_data["message"] += f" ({len(failed_cells)} failed)"
        
        return compact_json_response(response_data)
            
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }) 