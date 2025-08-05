"""Handler for deleting columns from tables in Google Sheets."""

from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
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
    Delete specific columns from a table in Google Sheets.
    
    According to the official Google Sheets API documentation, to delete columns from a table:
    1. Use DeleteRangeRequest to delete the column from the sheet (within the table's range)
    2. Use UpdateTableRequest to update the table's range and column properties to reflect the column removal
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete columns from
        column_names: List of column names to delete
    
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
        
        if not column_names or len(column_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "Column names are required. Please provide at least one column name to delete."
            })
        
        # Validate column names
        validated_column_names = []
        invalid_column_names = []
        
        for i, col_name in enumerate(column_names):
            if not col_name or not isinstance(col_name, str) or col_name.strip() == "":
                invalid_column_names.append({"index": i, "value": col_name, "error": "Column name must be a non-empty string"})
                continue
            
            validated_column_names.append(col_name.strip())
        
        if invalid_column_names:
            error_messages = [f"Column {item['index']+1} ('{item['value']}'): {item['error']}" for item in invalid_column_names]
            return compact_json_response({
                "success": False,
                "message": f"Invalid column names: {'; '.join(error_messages)}",
                "invalid_column_names": invalid_column_names
            })
        
        if not validated_column_names:
            return compact_json_response({
                "success": False,
                "message": "No valid column names provided after validation."
            })
        
        # Remove duplicates
        unique_column_names = list(set(validated_column_names))
        
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
            existing_columns = table_info.get("columns", [])
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
        
        # Validate column names exist in the table
        existing_column_names = [col.get("name", "") for col in existing_columns]
        missing_columns = []
        valid_delete_columns = []
        
        for col_name in unique_column_names:
            if col_name not in existing_column_names:
                missing_columns.append(col_name)
            else:
                valid_delete_columns.append(col_name)
        
        if missing_columns:
            return compact_json_response({
                "success": False,
                "message": f"Column(s) not found in table: {', '.join(missing_columns)}. Available columns: {', '.join(existing_column_names)}",
                "missing_columns": missing_columns,
                "available_columns": existing_column_names
            })
        
        if not valid_delete_columns:
            return compact_json_response({
                "success": False,
                "message": "No valid columns to delete after validation."
            })
        
        # Check if trying to delete all columns
        if len(valid_delete_columns) >= len(existing_columns):
            return compact_json_response({
                "success": False,
                "message": "Cannot delete all columns from a table. At least one column must remain."
            })
        
        # Create requests for deletion and table update
        requests = []
        
        # 1. Delete columns using DeleteRangeRequest (rightmost to leftmost to avoid index shifting)
        # Sort columns by their index in descending order
        columns_to_delete = []
        for col_name in valid_delete_columns:
            for i, col_info in enumerate(existing_columns):
                if col_info.get("name") == col_name:
                    columns_to_delete.append({
                        "name": col_name,
                        "index": col_info.get("index", i),
                        "api_index": table_start_col + col_info.get("index", i)
                    })
                    break
        
        # Sort by index in descending order for proper deletion
        columns_to_delete.sort(key=lambda x: x["index"], reverse=True)
        
        # Create DeleteRangeRequest for each column
        for col_info in columns_to_delete:
            delete_request = {
                "deleteRange": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": table_end_row,
                        "startColumnIndex": col_info["api_index"],
                        "endColumnIndex": col_info["api_index"] + 1
                    },
                    "shiftDimension": "COLUMNS"
                }
            }
            requests.append(delete_request)
        
        # 2. Update table with new column properties
        # Build new column properties array (excluding deleted columns)
        new_column_properties = []
        remaining_columns = []
        
        for col_info in existing_columns:
            if col_info.get("name") not in valid_delete_columns:
                remaining_columns.append(col_info)
        
        # Convert remaining columns to API format and update indices
        for i, col_info in enumerate(remaining_columns):
            api_col_prop = {
                "columnIndex": i,
                "columnName": col_info.get("name", ""),
                "columnType": col_info.get("type", "TEXT")
            }
            # Preserve dataValidationRule if it exists
            if "dataValidationRule" in col_info:
                api_col_prop["dataValidationRule"] = col_info["dataValidationRule"]
            new_column_properties.append(api_col_prop)
        
        # Update table range and column properties
        new_end_col = table_end_col - len(valid_delete_columns)
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_start_row,
                        "endRowIndex": table_end_row,
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": new_end_col
                    },
                    "columnProperties": new_column_properties
                },
                "fields": "range,columnProperties"
            }
        }
        requests.append(update_table_request)
        
        # Execute the requests
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        deleted_count = len(valid_delete_columns)
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "columns_deleted": deleted_count,
            "deleted_column_names": valid_delete_columns,
            "remaining_column_count": len(new_column_properties),
            "remaining_columns": [col.get("columnName", "") for col in new_column_properties],
            "message": f"Successfully deleted {deleted_count} column(s) from table '{table_name}' in '{sheet_name}'"
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
            "message": f"Error deleting table columns: {str(e)}"
        }) 