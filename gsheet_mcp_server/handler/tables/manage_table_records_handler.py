"""Handler for modifying table data in Google Sheets."""

from typing import List, Any, Dict, Optional
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names, get_table_info
from gsheet_mcp_server.helper.json_utils import compact_json_response


def modify_table_data_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    operation: str,
    data: List[List[Any]] = [],
    row_index: Optional[int] = None,
    row_indices: List[int] = []
) -> str:
    """
    Modify data in a table in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to modify
        operation: Type of operation ('append', 'insert', 'remove')
        data: List of rows to add/insert (each row is a list of values)
        row_index: Index for insert operation (0-based)
        row_indices: List of row indices to remove (0-based, header is row 0)
    
    Returns:
        str: Success message with operation details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required and cannot be empty."
            })
        
        if operation not in ["append", "insert", "remove"]:
            return compact_json_response({
                "success": False,
                "message": f"Invalid operation '{operation}'. Valid operations: append, insert, remove"
            })
        
        # Validate data for append/insert operations
        if operation in ["append", "insert"]:
            if not data or len(data) == 0:
                return compact_json_response({
                    "success": False,
                    "message": f"Data is required for '{operation}' operation."
                })
        
        # Validate row_index for insert operation
        if operation == "insert":
            if row_index is None:
                return compact_json_response({
                    "success": False,
                    "message": "row_index is required for insert operation."
                })
            if row_index < 0:
                return compact_json_response({
                    "success": False,
                    "message": "row_index must be 0 or greater."
                })
        
        # Validate row_indices for remove operation
        if operation == "remove":
            if not row_indices or len(row_indices) == 0:
                return compact_json_response({
                    "success": False,
                    "message": "row_indices is required for remove operation."
                })
            for idx in row_indices:
                if idx < 0:
                    return compact_json_response({
                        "success": False,
                        "message": "All row_indices must be 0 or greater."
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
        
        # Prepare batch update requests
        requests = []
        
        if operation == "append":
            # Append rows at the end of the table
            append_row = table_start_row + current_row_count
            
            # Create append request
            append_request = {
                "appendCells": {
                    "sheetId": sheet_id,
                    "rows": [{"values": [{"userEnteredValue": {"stringValue": cell}} for cell in row]} for row in data],
                    "fields": "userEnteredValue"
                }
            }
            requests.append(append_request)
            
            # Update table range to include new rows
            new_end_row = table_end_row + len(data)
            update_table_request = {
                "updateTable": {
                    "table": {
                        "tableId": table_id,
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": table_start_row,
                            "endRowIndex": new_end_row,
                            "startColumnIndex": table_start_col,
                            "endColumnIndex": table_end_col
                        }
                    },
                    "fields": "range"
                }
            }
            requests.append(update_table_request)
            
        elif operation == "insert":
            # Insert rows at specific position (table-specific)
            # Add 1 to skip the header row (row_index is 0-based for data rows)
            insert_row = table_start_row + row_index + 1
            
            # First, expand the table range to accommodate new rows
            new_end_row = table_end_row + len(data)
            expand_table_request = {
                "updateTable": {
                    "table": {
                        "tableId": table_id,
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": table_start_row,
                            "endRowIndex": new_end_row,
                            "startColumnIndex": table_start_col,
                            "endColumnIndex": table_end_col
                        }
                    },
                    "fields": "range"
                }
            }
            requests.append(expand_table_request)
            
            # Execute the range update first to ensure the table is expanded
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [expand_table_request]}
            ).execute()
            
            # Insert the data at the specific position
            insert_data_request = {
                "updateCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": insert_row,
                        "endRowIndex": insert_row + len(data),
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": table_end_col
                    },
                    "rows": [{"values": [{"userEnteredValue": {"stringValue": cell}} for cell in row]} for row in data],
                    "fields": "userEnteredValue"
                }
            }
            requests.append(insert_data_request)
            
        elif operation == "remove":
            # Remove specific rows by clearing table cells only (table-specific)
            # Sort indices in descending order to avoid shifting issues
            sorted_indices = sorted(row_indices, reverse=True)
            
            # Clear the specific table cells for each row to be removed
            for row_idx in sorted_indices:
                # Calculate actual row position in sheet
                # Add 1 to skip the header row (row_idx is 0-based for data rows)
                sheet_row_index = table_start_row + row_idx + 1
                
                # Clear only the table cells (not the entire row)
                clear_request = {
                    "updateCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": sheet_row_index,
                            "endRowIndex": sheet_row_index + 1,
                            "startColumnIndex": table_start_col,
                            "endColumnIndex": table_end_col
                        },
                        "rows": [{"values": [{"userEnteredValue": {"stringValue": ""}} for _ in range(table_end_col - table_start_col)]}],
                        "fields": "userEnteredValue"
                    }
                }
                requests.append(clear_request)
            
            # Update table range to exclude the "removed" rows
            new_end_row = table_end_row - len(row_indices)
            update_table_request = {
                "updateTable": {
                    "table": {
                        "tableId": table_id,
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": table_start_row,
                            "endRowIndex": new_end_row,
                            "startColumnIndex": table_start_col,
                            "endColumnIndex": table_end_col
                        }
                    },
                    "fields": "range"
                }
            }
            requests.append(update_table_request)
        
        # Execute batch update
        if operation == "insert":
            # For insert, we already executed the range update, so only execute the data insertion
            remaining_requests = [req for req in requests if "updateTable" not in req]
            if remaining_requests:
                batch_request = {"requests": remaining_requests}
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=batch_request
                ).execute()
        else:
            # For other operations, execute all requests
            batch_request = {"requests": requests}
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=batch_request
            ).execute()
        
        # Prepare response message
        if operation == "append":
            message = f"Successfully appended {len(data)} row(s) to table '{table_name}' in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        elif operation == "insert":
            message = f"Successfully inserted {len(data)} row(s) at position {row_index} in table '{table_name}' in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        else:  # remove
            message = f"Successfully removed {len(row_indices)} row(s) from table '{table_name}' in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        
        return compact_json_response({
            "success": True,
            "message": message,
            "data": {
                "operation": operation,
                "table_name": table_name,
                "sheet_name": sheet_name,
                "spreadsheet_name": spreadsheet_name,
                "data_rows": len(data) if operation in ["append", "insert"] else 0,
                "removed_rows": len(row_indices) if operation == "remove" else 0,
                "insert_position": row_index if operation == "insert" else None
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error modifying table data: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }) 