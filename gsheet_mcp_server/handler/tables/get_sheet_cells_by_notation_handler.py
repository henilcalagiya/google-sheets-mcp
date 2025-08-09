"""Handler for getting individual cell values from sheets in Google Sheets."""

from typing import List, Dict, Any, Optional, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import parse_cell_reference
from gsheet_mcp_server.helper.json_utils import compact_json_response

def get_sheet_cells_by_notation_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    cell_notations: List[str]
) -> str:
    """
    Get values from specific cells in a sheet in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to get cells from
        cell_notations: List of cell notations (e.g., ['A1', 'A6', 'A10', 'E5'])
    
    Returns:
        str: Success message with cell values and mapping or error message
    """
    try:
        # Validate inputs
        if not cell_notations or not isinstance(cell_notations, list):
            return compact_json_response({
                "success": False,
                "message": "Cell notations are required and must be a list."
            })
        
        if len(cell_notations) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one cell notation is required."
            })
        
        # Validate cell notations
        valid_notations = []
        invalid_notations = []
        
        for notation in cell_notations:
            if not isinstance(notation, str) or not notation.strip():
                invalid_notations.append({"notation": notation, "error": "Invalid cell notation"})
                continue
            
            try:
                # Validate A1 notation format
                row_idx, col_idx = parse_cell_reference(notation.strip())
                valid_notations.append(notation.strip())
            except ValueError:
                invalid_notations.append({"notation": notation, "error": "Invalid A1 notation format"})
        
        if invalid_notations:
            error_messages = [f"'{item['notation']}': {item['error']}" for item in invalid_notations]
            return compact_json_response({
                "success": False,
                "message": f"Invalid cell notations: {'; '.join(error_messages)}",
                "invalid_notations": invalid_notations
            })
        
        if not valid_notations:
            return compact_json_response({
                "success": False,
                "message": "No valid cell notations provided."
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
        cell_values = {}
        cell_data = {}
        
        try:
            # Get values for each cell notation separately
            for notation in valid_notations:
                range_notation = f"'{sheet_name}'!{notation}"
                response = sheets_service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=range_notation
                ).execute()
                
                values = response.get('values', [])
                cell_value = values[0][0] if values and values[0] else None
                
                cell_values[notation] = cell_value
                cell_data[notation] = {
                    "value": cell_value,
                    "notation": notation
                }
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            return compact_json_response({
                "success": False,
                "message": f"Failed to retrieve cell values: {error_details}",
                "error_code": e.resp.status if hasattr(e, 'resp') else None
            })
        
        # Prepare response
        response_data = {
            "success": True,
            "message": f"Successfully retrieved {len(cell_values)} cell values from sheet '{sheet_name}'",
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "cell_count": len(cell_values),
            "cell_data": cell_data,
            "summary": {
                "total_cells": len(cell_values),
                "non_empty_cells": len([v for v in cell_values.values() if v is not None]),
                "empty_cells": len([v for v in cell_values.values() if v is None])
            }
        }
        
        return compact_json_response(response_data)
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        })
