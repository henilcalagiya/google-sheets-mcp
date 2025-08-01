"""Handler for changing column properties in existing tables in Google Sheets."""

from typing import List, Any, Dict, Optional
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names, get_table_info
from gsheet_mcp_server.helper.json_utils import compact_json_response


def modify_column_properties_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_name: str,
    new_column_name: str = "",
    new_column_type: str = "",
    new_dropdown_options: List[str] = [],
    remove_dropdown: bool = False,
    add_dropdown_options: List[str] = [],
    remove_dropdown_options: List[str] = []
) -> str:
    """
    Change properties of an existing column in a table in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table containing the column
        column_name: Name of the column to change
        new_column_name: New name for the column (optional)
        new_column_type: New type for the column (optional)
        new_dropdown_options: New dropdown options (optional)
        remove_dropdown: Whether to remove dropdown validation (default: False)
    
    Returns:
        str: Success message with change details
    """
    try:
        # Validate inputs
        if not column_name or column_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Column name is required and cannot be empty."
            })
        
        # Check if at least one property is being changed
        has_changes = False
        if new_column_name and new_column_name.strip():
            has_changes = True
        if new_column_type and new_column_type.strip():
            has_changes = True
        if new_dropdown_options and len(new_dropdown_options) > 0:
            has_changes = True
        if remove_dropdown:
            has_changes = True
        if add_dropdown_options and len(add_dropdown_options) > 0:
            has_changes = True
        if remove_dropdown_options and len(remove_dropdown_options) > 0:
            has_changes = True
            
        if not has_changes:
            return compact_json_response({
                "success": False,
                "message": "At least one property must be specified for change (new_column_name, new_column_type, new_dropdown_options, add_dropdown_options, remove_dropdown_options, or remove_dropdown)."
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
            columns = table_info.get('columns', [])
        except RuntimeError as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Find the column to change
        target_column = None
        column_index = None
        for col in columns:
            if col['name'] == column_name:
                target_column = col
                column_index = col['index']
                break
        
        if target_column is None:
            return compact_json_response({
                "success": False,
                "message": f"Column '{column_name}' not found in table '{table_name}'."
            })
        
        # Validate new column name if provided
        if new_column_name and new_column_name.strip():
            from gsheet_mcp_server.handler.tables.add_table_column_handler import _clean_column_name
            cleaned_new_name = _clean_column_name(new_column_name)
            if not cleaned_new_name:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid new column name '{new_column_name}'. Please provide a valid name."
                })
            new_column_name = cleaned_new_name
        else:
            new_column_name = None
        
        # Validate new column type if provided
        if new_column_type and new_column_type.strip():
            valid_types = ["TEXT", "NUMBER", "DATE", "TIME", "DATE_TIME", "BOOLEAN", "PERCENT", "CURRENCY", "DROPDOWN", "NONE"]
            if new_column_type not in valid_types:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid column type '{new_column_type}'. Valid types: {', '.join(valid_types)}"
                })
        else:
            new_column_type = None
        
        # Map user-friendly types to Google Sheets API types
        api_type_mapping = {
            "TEXT": "TEXT",
            "NUMBER": "DOUBLE",
            "DATE": "DATE",
            "TIME": "TIME",
            "DATE_TIME": "DATE_TIME",
            "BOOLEAN": "BOOLEAN",
            "PERCENT": "PERCENT",
            "CURRENCY": "CURRENCY",
            "DROPDOWN": "DROPDOWN",
            "NONE": "COLUMN_TYPE_UNSPECIFIED"
        }
        
        # Prepare the updated column property for the target column
        updated_column_property = {
            "columnIndex": column_index,
            "columnName": new_column_name if new_column_name else target_column['name'],
            "columnType": api_type_mapping.get(new_column_type, target_column['type']) if new_column_type else target_column['type']
        }
        
        # Handle dropdown validation changes
        if remove_dropdown:
            # Remove dropdown validation - don't add dataValidationRule at all
            pass  # Simply don't include dataValidationRule in the property
        elif new_dropdown_options and len(new_dropdown_options) > 0:
            # Add or update dropdown validation with new options
            updated_column_property["dataValidationRule"] = {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": opt} for opt in new_dropdown_options]
                }
            }
            # Ensure column type is DROPDOWN if validation is specified
            if updated_column_property["columnType"] == "TEXT":
                updated_column_property["columnType"] = "DROPDOWN"
        elif add_dropdown_options and len(add_dropdown_options) > 0:
            # Add new options to existing dropdown
            current_options = []
            if 'dataValidationRule' in target_column:
                # Extract current options from existing validation
                current_validation = target_column['dataValidationRule']
                if 'condition' in current_validation and 'values' in current_validation['condition']:
                    current_options = [val.get('userEnteredValue', '') for val in current_validation['condition']['values']]
            
            # Add new options (avoid duplicates)
            for option in add_dropdown_options:
                if option not in current_options:
                    current_options.append(option)
            
            # Create new validation rule with combined options
            updated_column_property["dataValidationRule"] = {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": opt} for opt in current_options]
                }
            }
            # Ensure column type is DROPDOWN
            if updated_column_property["columnType"] == "TEXT":
                updated_column_property["columnType"] = "DROPDOWN"
        elif remove_dropdown_options and len(remove_dropdown_options) > 0:
            # Remove specific options from existing dropdown
            current_options = []
            if 'dataValidationRule' in target_column:
                # Extract current options from existing validation
                current_validation = target_column['dataValidationRule']
                if 'condition' in current_validation and 'values' in current_validation['condition']:
                    current_options = [val.get('userEnteredValue', '') for val in current_validation['condition']['values']]
            
            # Remove specified options
            for option in remove_dropdown_options:
                if option in current_options:
                    current_options.remove(option)
            
            # Create new validation rule with remaining options
            if current_options:
                updated_column_property["dataValidationRule"] = {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": opt} for opt in current_options]
                    }
                }
                # Ensure column type is DROPDOWN
                if updated_column_property["columnType"] == "TEXT":
                    updated_column_property["columnType"] = "DROPDOWN"
            else:
                # If no options left, remove dropdown entirely
                pass  # Don't include dataValidationRule
        else:
            # Preserve existing dropdown validation if no new options provided
            if 'dataValidationRule' in target_column:
                updated_column_property["dataValidationRule"] = target_column['dataValidationRule']
        
        # Prepare all column properties - include all existing columns but update only the target column
        all_column_properties = []
        for col in columns:
            if col['index'] == column_index:
                # This is the column we want to change
                all_column_properties.append(updated_column_property)
            else:
                # Keep other columns unchanged - preserve their existing properties including validation
                other_column_property = {
                    "columnIndex": col['index'],
                    "columnName": col['name'],
                    "columnType": col['type']
                }
                # If this column has existing validation, preserve it
                if 'dataValidationRule' in col:
                    other_column_property['dataValidationRule'] = col['dataValidationRule']
                all_column_properties.append(other_column_property)
        
        # Create update table request with all columns
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "columnProperties": all_column_properties
                },
                "fields": "columnProperties"
            }
        }
        
        # Update header cell if column name is changing
        requests = [update_table_request]
        if new_column_name:
            table_start_row = table_info.get('start_row', 0)
            table_start_col = table_info.get('start_col', 0)
            sheet_column_position = table_start_col + column_index
            
            header_update_request = {
                "updateCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_start_row,
                        "endRowIndex": table_start_row + 1,
                        "startColumnIndex": sheet_column_position,
                        "endColumnIndex": sheet_column_position + 1
                    },
                    "rows": [{"values": [{"userEnteredValue": {"stringValue": new_column_name}}]}],
                    "fields": "userEnteredValue"
                }
            }
            requests.append(header_update_request)
        
        # Execute batch update
        batch_request = {
            "requests": requests
        }
        
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_request
        ).execute()
        
        # Prepare response message
        changes = []
        if new_column_name:
            changes.append(f"name to '{new_column_name}'")
        if new_column_type:
            changes.append(f"type to '{new_column_type}'")
        if new_dropdown_options and len(new_dropdown_options) > 0:
            changes.append(f"dropdown options to {len(new_dropdown_options)} options")
        if add_dropdown_options and len(add_dropdown_options) > 0:
            changes.append(f"added {len(add_dropdown_options)} dropdown options")
        if remove_dropdown_options and len(remove_dropdown_options) > 0:
            changes.append(f"removed {len(remove_dropdown_options)} dropdown options")
        if remove_dropdown:
            changes.append("removed dropdown validation")
        
        change_text = ", ".join(changes)
        message = f"Successfully changed column '{column_name}' {change_text} in table '{table_name}' in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        
        return compact_json_response({
            "success": True,
            "message": message,
            "data": {
                "column_name": column_name,
                "new_column_name": new_column_name,
                "new_column_type": new_column_type,
                "new_dropdown_options": new_dropdown_options,
                "add_dropdown_options": add_dropdown_options,
                "remove_dropdown_options": remove_dropdown_options,
                "remove_dropdown": remove_dropdown,
                "table_name": table_name,
                "sheet_name": sheet_name,
                "spreadsheet_name": spreadsheet_name,
                "changes_made": changes
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error changing column property: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }) 