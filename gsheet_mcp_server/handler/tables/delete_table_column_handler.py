"""Handler for deleting columns from existing tables in Google Sheets."""

from typing import List, Any, Dict
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names, get_table_info
from gsheet_mcp_server.helper.json_utils import compact_json_response


def delete_table_column_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_names: List[str]
) -> str:
    """
    Delete columns from an existing table in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete columns from
        column_names: List of column names to delete
    
    Returns:
        str: Success message with deletion details
    """
    try:
        # Validate inputs
        if not column_names or len(column_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one column name must be provided for deletion."
            })
        
        # Get spreadsheet ID using utility function
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })

        # Get sheet ID using utility function
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
        
        # Get current table information
        try:
            table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
            current_column_count = table_info.get('column_count', 0)
            table_start_col = table_info.get('start_col', 0)
            columns = table_info.get('columns', [])
        except RuntimeError as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Validate that we're not deleting all columns
        if len(column_names) >= current_column_count:
            return compact_json_response({
                "success": False,
                "message": f"Cannot delete all columns from table '{table_name}'. At least one column must remain."
            })
        
        # Get sheet ID for delete dimension operation
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        
        # Prepare batch update requests
        requests = []
        deleted_columns = []
        failed_columns = []
        
        # Find actual column positions by name
        column_positions = []
        found_columns = []
        
        for col_name in column_names:
            column_found = False
            for col in columns:
                if col['name'] == col_name:
                    column_positions.append(col['index'])
                    found_columns.append(col_name)
                    column_found = True
                    break
            
            if not column_found:
                failed_columns.append(col_name)
        
        # Sort positions in descending order to avoid shifting issues
        sorted_positions = sorted(column_positions, reverse=True)
        
        for position in sorted_positions:
            # Calculate the actual column position in the sheet
            sheet_column_position = table_start_col + position
            
            # Create delete dimension request
            delete_request = {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": sheet_column_position,
                        "endIndex": sheet_column_position + 1
                    }
                }
            }
            requests.append(delete_request)
            
            # Find the column name for this position
            for col in columns:
                if col['index'] == position:
                    deleted_columns.append(col['name'])
                    break
        
        # Execute batch update
        if requests:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests}
            ).execute()
        
        # Prepare response
        success_message = f"Successfully deleted {len(deleted_columns)} column(s) from table '{table_name}' in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        
        if failed_columns:
            success_message += f" Failed to delete: {', '.join(failed_columns)}"
        
        return compact_json_response({
            "success": True,
            "message": success_message,
            "data": {
                "deleted_columns": deleted_columns,
                "failed_columns": failed_columns,
                "table_name": table_name,
                "sheet_name": sheet_name,
                "spreadsheet_name": spreadsheet_name,
                "total_deleted": len(deleted_columns),
                "total_failed": len(failed_columns)
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error deleting table columns: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }) 