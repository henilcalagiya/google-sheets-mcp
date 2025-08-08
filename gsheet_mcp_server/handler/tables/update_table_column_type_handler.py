"""Handler for updating table column types in Google Sheets."""

from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    validate_column_type,
    map_column_type,
    get_number_format_for_type
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def update_table_column_type_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_names: List[str],
    new_column_types: List[str]
) -> str:
    """
    Update column types in a table in Google Sheets using the official updateTable operation.
    
    According to the official Google Sheets API documentation, to update column types:
    1. Use UpdateTableRequest to update column properties with new types
    2. Apply proper formatting to existing data based on new types
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update column types in
        column_names: List of column names to update types for
        new_column_types: List of new column types (must match column_names count)
    
    Returns:
        str: Success message with type update details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if not column_names or not isinstance(column_names, list):
            return compact_json_response({
                "success": False,
                "message": "Column names are required and must be a list."
            })
        
        if not new_column_types or not isinstance(new_column_types, list):
            return compact_json_response({
                "success": False,
                "message": "New column types are required and must be a list."
            })
        
        if len(column_names) != len(new_column_types):
            return compact_json_response({
                "success": False,
                "message": "Number of column names must match number of new column types."
            })
        
        # Validate column names and types
        validated_changes = []
        invalid_changes = []
        
        for i, (col_name, col_type) in enumerate(zip(column_names, new_column_types)):
            if not col_name or not isinstance(col_name, str) or col_name.strip() == "":
                invalid_changes.append({"index": i, "column": col_name, "error": "Column name cannot be empty"})
                continue
            
            # Validate column type
            type_validation = validate_column_type(col_type)
            if not type_validation["valid"]:
                invalid_changes.append({"index": i, "column": col_name, "error": type_validation["error"]})
                continue
            
            validated_changes.append({
                "column_name": col_name.strip(),
                "new_type": type_validation["cleaned_type"]
            })
        
        if invalid_changes:
            error_messages = [f"Change {item['index']+1} ({item['column']}): {item['error']}" for item in invalid_changes]
            return compact_json_response({
                "success": False,
                "message": f"Invalid column type changes: {'; '.join(error_messages)}",
                "invalid_changes": invalid_changes
            })
        
        if not validated_changes:
            return compact_json_response({
                "success": False,
                "message": "No valid column type changes provided after validation."
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
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Create mapping of column names to new types
        type_mapping = {change["column_name"]: change["new_type"] for change in validated_changes}
        
        # Validate that all specified columns exist in the table
        existing_column_names = [col.get("name", "") for col in columns]
        missing_columns = []
        valid_changes = []
        
        for change in validated_changes:
            if change["column_name"] not in existing_column_names:
                missing_columns.append(change["column_name"])
            else:
                valid_changes.append(change)
        
        if missing_columns:
            return compact_json_response({
                "success": False,
                "message": f"Column(s) not found in table: {', '.join(missing_columns)}"
            })
        
        if not valid_changes:
            return compact_json_response({
                "success": False,
                "message": "No valid column type changes after validation."
            })
        
        # Create batch update requests
        requests = []
        
        # Convert existing columns to API format and update column types
        updated_column_properties = []
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "TEXT")
            col_index = col.get("index", 0)
            
            # Create API format column property
            api_col_prop = {
                "columnIndex": col_index,
                "columnName": col_name,
                "columnType": map_column_type(type_mapping.get(col_name, col_type))  # Use new type if in mapping, otherwise keep existing
            }
            
            # Preserve existing dataValidationRule if it exists and column type isn't being changed
            if "dataValidationRule" in col and col_name not in type_mapping:
                api_col_prop["dataValidationRule"] = col["dataValidationRule"]
            
            updated_column_properties.append(api_col_prop)
        
        # Update table with new column properties
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "columnProperties": updated_column_properties
                },
                "fields": "columnProperties.columnName,columnProperties.columnType"
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
        successful_changes = len(valid_changes)
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "columns_updated": successful_changes,
            "type_changes": valid_changes,
            "message": f"Successfully changed types for {successful_changes} column(s) in table '{table_name}' in '{sheet_name}'"
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
            "message": f"Error changing table column types: {str(e)}"
        }) 