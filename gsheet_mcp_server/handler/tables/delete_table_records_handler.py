"""Handler for deleting specific rows from tables in Google Sheets."""

from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def delete_table_records_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    row_indices: List[int]
) -> str:
    """
    Delete specific records (rows) from a table in Google Sheets using DeleteRangeRequest and UpdateTableRequest.
    
    According to the official Google Sheets API documentation, to delete records from a table:
    1. Use DeleteRangeRequest to remove specific rows from the sheet
    2. Use UpdateTableRequest to shrink the table's range to exclude deleted rows
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete records from
        row_indices: List of row indices to delete (1-based, excluding header)
    
    Returns:
        str: Success message with deletion details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if not row_indices or len(row_indices) == 0:
            return compact_json_response({
                "success": False,
                "message": "Row indices are required. Please provide at least one row index to delete."
            })
        
        # Validate row indices
        validated_indices = []
        invalid_indices = []
        
        for i, row_index in enumerate(row_indices):
            if not isinstance(row_index, int):
                invalid_indices.append({"index": i, "value": row_index, "error": "Row index must be an integer"})
                continue
            
            if row_index < 1:
                invalid_indices.append({"index": i, "value": row_index, "error": "Row index must be 1 or greater"})
                continue
            
            validated_indices.append(row_index)
        
        if invalid_indices:
            error_messages = [f"Row {item['index']+1} ({item['value']}): {item['error']}" for item in invalid_indices]
            return compact_json_response({
                "success": False,
                "message": f"Invalid row indices: {'; '.join(error_messages)}",
                "invalid_indices": invalid_indices
            })
        
        if not validated_indices:
            return compact_json_response({
                "success": False,
                "message": "No valid row indices provided after validation."
            })
        
        # Remove duplicates and sort in descending order (to avoid index shifting)
        unique_indices = list(set(validated_indices))
        unique_indices.sort(reverse=True)
        
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
            table_range = table_info.get("range", {})
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
        
        # Validate row indices are within table range
        invalid_range_indices = []
        valid_delete_requests = []
        
        for row_index in unique_indices:
            # Convert 1-based user index to 0-based API index (accounting for header)
            api_row_index = table_start_row + row_index
            
            if api_row_index < table_start_row or api_row_index >= table_end_row:
                invalid_range_indices.append({
                    "row_index": row_index,
                    "error": f"Row {row_index} is outside table range (1 to {table_end_row - table_start_row - 1})"
                })
            else:
                # Create DeleteRangeRequest for this row
                delete_range_request = {
                    "deleteRange": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": api_row_index,
                            "endRowIndex": api_row_index + 1,
                            "startColumnIndex": table_start_col,
                            "endColumnIndex": table_end_col
                        },
                        "shiftDimension": "ROWS"
                    }
                }
                valid_delete_requests.append(delete_range_request)
        
        if invalid_range_indices:
            error_messages = [f"Row {item['row_index']}: {item['error']}" for item in invalid_range_indices]
            return compact_json_response({
                "success": False,
                "message": f"Invalid row indices: {'; '.join(error_messages)}",
                "invalid_range_indices": invalid_range_indices
            })
        
        if not valid_delete_requests:
            return compact_json_response({
                "success": False,
                "message": "No valid rows to delete after range validation."
            })
        
        # Use only delete range requests
        all_requests = valid_delete_requests
        
        # Execute the batch update requests
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": all_requests}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        delete_count = len(valid_delete_requests)
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "rows_deleted": delete_count,
            "deleted_row_indices": unique_indices,
            "message": f"Successfully deleted {delete_count} row(s) from table '{table_name}' in '{sheet_name}'"
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
            "message": f"Error deleting table rows: {str(e)}"
        }) 