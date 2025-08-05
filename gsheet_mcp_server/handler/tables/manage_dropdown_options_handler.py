"""Handler for managing dropdown options in table columns in Google Sheets."""

from typing import List, Dict, Union, Optional
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def manage_dropdown_options_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    action: str,
    column_names: List[str],
    dropdown_options: Optional[List[List[str]]] = None
) -> str:
    """
    Manage dropdown options in table columns in Google Sheets using the official updateTable operation.
    
    According to the official Google Sheets API documentation, to manage dropdown options:
    1. Use UpdateTableRequest to update column properties with data validation rules
    2. Set the column type to DROPDOWN and add validation options, or remove validation
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to manage dropdown options in
        action: Action to perform - "add" or "remove"
        column_names: List of column names to manage dropdown options for
        dropdown_options: List of dropdown options to add/remove for each column:
            - For "add" action: List of new options to add to existing dropdown
            - For "remove" action: List of options to remove from existing dropdown
    
    Returns:
        str: Success message with dropdown management details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if action not in ["add", "remove"]:
            return compact_json_response({
                "success": False,
                "message": "Action must be 'add' or 'remove'."
            })
        
        if not column_names or not isinstance(column_names, list):
            return compact_json_response({
                "success": False,
                "message": "Column names are required and must be a list."
            })
        
        # Validate dropdown options for add/remove actions
        if action in ["add", "remove"]:
            if not dropdown_options or not isinstance(dropdown_options, list):
                return compact_json_response({
                    "success": False,
                    "message": f"Dropdown options are required for '{action}' action and must be a list."
                })
            
            if len(column_names) != len(dropdown_options):
                return compact_json_response({
                    "success": False,
                    "message": "Number of column names must match number of dropdown options lists."
                })
        
        # Validate column names
        validated_columns = []
        invalid_columns = []
        
        for i, col_name in enumerate(column_names):
            if not col_name or not isinstance(col_name, str) or col_name.strip() == "":
                invalid_columns.append({"index": i, "column": col_name, "error": "Column name cannot be empty"})
                continue
            
            validated_columns.append(col_name.strip())
        
        if invalid_columns:
            error_messages = [f"Column {item['index']+1} '{item['column']}': {item['error']}" for item in invalid_columns]
            return compact_json_response({
                "success": False,
                "message": f"Invalid columns: {'; '.join(error_messages)}",
                "invalid_columns": invalid_columns
            })
        
        if not validated_columns:
            return compact_json_response({
                "success": False,
                "message": "No valid columns provided after validation."
            })
        
        # Validate dropdown options for add/remove actions
        validated_operations = []
        if action in ["add", "remove"]:
            for i, (col_name, options) in enumerate(zip(validated_columns, dropdown_options)):
                if not isinstance(options, list):
                    invalid_columns.append({"index": i, "column": col_name, "error": "Dropdown options must be a list"})
                    continue
                
                if not options:
                    invalid_columns.append({"index": i, "column": col_name, "error": "Dropdown options cannot be empty"})
                    continue
                
                # Validate individual options
                valid_options = []
                invalid_options = []
                
                for j, option in enumerate(options):
                    if not isinstance(option, str) or option.strip() == "":
                        invalid_options.append({"option_index": j, "option": option, "error": "Option cannot be empty"})
                    else:
                        valid_options.append(option.strip())
                
                if invalid_options:
                    error_messages = [f"Option {item['option_index']+1}: {item['error']}" for item in invalid_options]
                    invalid_columns.append({"index": i, "column": col_name, "error": f"Invalid options: {'; '.join(error_messages)}"})
                    continue
                
                if not valid_options:
                    invalid_columns.append({"index": i, "column": col_name, "error": "No valid options provided"})
                    continue
                
                validated_operations.append({
                    "column_name": col_name,
                    "options": valid_options
                })
            
            if invalid_columns:
                error_messages = [f"Column '{item['column']}': {item['error']}" for item in invalid_columns]
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid dropdown configurations: {'; '.join(error_messages)}",
                    "invalid_columns": invalid_columns
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
        
        # Validate that all specified columns exist in the table
        existing_column_names = [col.get("name", "") for col in columns]
        missing_columns = []
        valid_operations = []
        
        if action == "add":
            # For add action, check if columns exist
            dropdown_mapping = {operation["column_name"]: operation["options"] for operation in validated_operations}
            
            for operation in validated_operations:
                if operation["column_name"] not in existing_column_names:
                    missing_columns.append(operation["column_name"])
                else:
                    valid_operations.append(operation)
        elif action == "remove":
            # For remove action, check if columns exist and have dropdown validation
            for operation in validated_operations:
                col_name = operation["column_name"]
                if col_name not in existing_column_names:
                    missing_columns.append(col_name)
                else:
                    # Find the column and check if it has dropdown validation
                    for col in columns:
                        if col.get("name", "") == col_name:
                            col_type = col.get("type", "TEXT")
                            has_validation = "dataValidationRule" in col
                            
                            if col_type == "DROPDOWN" and has_validation:
                                valid_operations.append(operation)
                            else:
                                missing_columns.append(col_name)
                            break
        
        if missing_columns:
            return compact_json_response({
                "success": False,
                "message": f"Column(s) not found or invalid: {', '.join(missing_columns)}"
            })
        
        if not valid_operations:
            return compact_json_response({
                "success": False,
                "message": f"No valid {action} operations after validation."
            })
        
        # Create batch update requests
        requests = []
        
        # Update table column properties
        updated_columns = []
        for col in columns:
            col_name = col.get("name", "")
            col_index = col.get("index", 0)
            col_updated = False
            
            if action == "add":
                # Add dropdown validation or add options to existing dropdown
                for operation in valid_operations:
                    if operation["column_name"] == col_name:
                        # Get existing dropdown options if any
                        existing_options = []
                        if col.get("type") == "DROPDOWN" and "dataValidationRule" in col:
                            existing_values = col["dataValidationRule"].get("condition", {}).get("values", [])
                            existing_options = [val.get("userEnteredValue", "") for val in existing_values if val.get("userEnteredValue")]
                        
                        # Combine existing and new options, removing duplicates
                        all_options = list(set(existing_options + operation["options"]))
                        
                        updated_col = {
                            "columnIndex": col_index,
                            "columnName": col_name,
                            "columnType": "DROPDOWN",
                            "dataValidationRule": {
                                "condition": {
                                    "type": "ONE_OF_LIST",
                                    "values": [{"userEnteredValue": opt} for opt in all_options]
                                }
                            }
                        }
                        updated_columns.append(updated_col)
                        col_updated = True
                        break
            elif action == "remove":
                # Remove specific options from dropdown
                for operation in valid_operations:
                    if operation["column_name"] == col_name:
                        # Get existing dropdown options
                        existing_options = []
                        if col.get("type") == "DROPDOWN" and "dataValidationRule" in col:
                            existing_values = col["dataValidationRule"].get("condition", {}).get("values", [])
                            existing_options = [val.get("userEnteredValue", "") for val in existing_values if val.get("userEnteredValue")]
                        
                        # Remove specified options
                        options_to_remove = set(operation["options"])
                        remaining_options = [opt for opt in existing_options if opt not in options_to_remove]
                        
                        if remaining_options:
                            # Keep dropdown with remaining options
                            updated_col = {
                                "columnIndex": col_index,
                                "columnName": col_name,
                                "columnType": "DROPDOWN",
                                "dataValidationRule": {
                                    "condition": {
                                        "type": "ONE_OF_LIST",
                                        "values": [{"userEnteredValue": opt} for opt in remaining_options]
                                    }
                                }
                            }
                        else:
                            # Convert to TEXT if no options remain
                            updated_col = {
                                "columnIndex": col_index,
                                "columnName": col_name,
                                "columnType": "TEXT"
                            }
                        
                        updated_columns.append(updated_col)
                        col_updated = True
                        break
            
            if not col_updated:
                # Keep existing column unchanged - only include required fields
                updated_col = {
                    "columnIndex": col_index,
                    "columnName": col_name,
                    "columnType": col.get("type", "TEXT")
                }
                # Preserve dataValidationRule if it exists
                if "dataValidationRule" in col:
                    updated_col["dataValidationRule"] = col["dataValidationRule"]
                updated_columns.append(updated_col)
        
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "columnProperties": updated_columns
                },
                "fields": "columnProperties.dataValidationRule"
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
        successful_operations = len(valid_operations)
        
        if action == "add":
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "action": "add",
                "dropdowns_updated": successful_operations,
                "options_added": valid_operations,
                "message": f"Successfully added dropdown options to {successful_operations} column(s) in table '{table_name}' in '{sheet_name}'"
            }
        elif action == "remove":
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "action": "remove",
                "dropdowns_updated": successful_operations,
                "options_removed": valid_operations,
                "message": f"Successfully removed dropdown options from {successful_operations} column(s) in table '{table_name}' in '{sheet_name}'"
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
            "message": f"Error managing dropdown options: {str(e)}"
        }) 