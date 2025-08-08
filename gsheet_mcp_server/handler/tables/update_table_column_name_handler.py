"""Handler for updating table column names in Google Sheets."""

from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_table_column_name_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_indices: List[int],
    new_column_names: List[str]
) -> str:
    """
    Update column names in a table in Google Sheets using the official updateTable operation.
    
    According to the official Google Sheets API documentation, to update table column names:
    1. Use UpdateTableRequest to update column properties including column names
    2. Update both the column properties and header cells
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update column names in
        column_indices: List of column indices to update (0-based)
        new_column_names: List of new column names (must match column_indices count)
    
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
        
        if not column_indices or not isinstance(column_indices, list):
            return compact_json_response({
                "success": False,
                "message": "Column indices are required and must be a list."
            })
        
        if not new_column_names or not isinstance(new_column_names, list):
            return compact_json_response({
                "success": False,
                "message": "New column names are required and must be a list."
            })
        
        if len(column_indices) != len(new_column_names):
            return compact_json_response({
                "success": False,
                "message": "Number of column indices must match number of new column names."
            })
        
        # Validate column indices and names
        validated_renames = []
        invalid_renames = []
        
        for i, (col_index, new_name) in enumerate(zip(column_indices, new_column_names)):
            if not isinstance(col_index, int) or col_index < 0:
                invalid_renames.append({"index": i, "column_index": col_index, "error": "Column index must be a non-negative integer"})
                continue
            
            if not new_name or not isinstance(new_name, str) or new_name.strip() == "":
                invalid_renames.append({"index": i, "new_name": new_name, "error": "New column name cannot be empty"})
                continue
            
            validated_renames.append({
                "column_index": col_index,
                "new_name": new_name.strip()
            })
        
        if invalid_renames:
            error_messages = [f"Rename {item['index']+1}: {item['error']}" for item in invalid_renames]
            return compact_json_response({
                "success": False,
                "message": f"Invalid column renames: {'; '.join(error_messages)}",
                "invalid_renames": invalid_renames
            })
        
        if not validated_renames:
            return compact_json_response({
                "success": False,
                "message": "No valid column renames provided after validation."
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
            columns = table_info.get('columns', [])
            table_range = table_info.get('range', {})
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Validate that all column indices exist in the table
        existing_column_count = len(columns)
        invalid_indices = []
        valid_renames = []
        
        for rename in validated_renames:
            col_index = rename["column_index"]
            if col_index >= existing_column_count:
                invalid_indices.append(col_index)
            else:
                valid_renames.append(rename)
        
        if invalid_indices:
            return compact_json_response({
                "success": False,
                "message": f"Invalid column indices: {invalid_indices}. Table has {existing_column_count} columns (0-based indexing)."
            })
        
        if not valid_renames:
            return compact_json_response({
                "success": False,
                "message": "No valid column renames after validation."
            })
        
        # Create batch update requests
        requests = []
        
        # Create mapping of column indices to new names
        rename_mapping = {rename["column_index"]: rename["new_name"] for rename in valid_renames}
        
        # Convert existing columns to API format and update column names
        updated_column_properties = []
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "TEXT")
            col_index = col.get("index", 0)
            
            # Create API format column property
            api_col_prop = {
                "columnIndex": col_index,
                "columnName": rename_mapping.get(col_index, col_name),  # Use new name if in mapping, otherwise keep old
                "columnType": col_type
            }
            
            # Preserve dataValidationRule if it exists
            if "dataValidationRule" in col:
                api_col_prop["dataValidationRule"] = col["dataValidationRule"]
            
            updated_column_properties.append(api_col_prop)
        
        # Update table with new column properties
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "columnProperties": updated_column_properties
                },
                "fields": "columnProperties.columnName"
            }
        }
        requests.append(update_table_request)
        
        # Execute the batch update
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        successful_renames = len(valid_renames)
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "columns_renamed": successful_renames,
            "renames": valid_renames,
            "message": f"Successfully renamed {successful_renames} column(s) in table '{table_name}' in '{sheet_name}'"
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
            "message": f"Error renaming table columns: {str(e)}"
        }) 