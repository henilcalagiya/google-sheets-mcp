"""Handler for managing table column properties in Google Sheets."""

from typing import List, Dict, Optional, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    validate_column_type,
    map_column_type,
    validate_column_name
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def manage_column_properties_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_name: str,
    new_name: Optional[str] = None,
    new_type: Optional[str] = None,
    dropdown_options: Optional[List[str]] = None
) -> str:
    """
    Manage column properties in a table in Google Sheets using the official updateTable operation.
    
    This handler can update a single column's name, type, and dropdown options in one operation.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to manage columns in
        column_name: Name of the column to update
        new_name: New name for the column (optional)
        new_type: New type for the column (optional)
        dropdown_options: List of dropdown options (optional, for DROPDOWN type)
    
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
        
        # Validate inputs
        if not column_name or not isinstance(column_name, str) or column_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Column name is required and cannot be empty."
            })
        
        # Check that at least one property is being updated
        if (new_name is None or new_name.strip() == "") and (new_type is None or new_type.strip() == ""):
            return compact_json_response({
                "success": False,
                "message": "At least one property (new_name or new_type) must be specified."
            })
        
        # Validate new name if provided
        validated_name = None
        if new_name is not None and new_name.strip() != "":
            name_validation = validate_column_name(new_name)
            if not name_validation["valid"]:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid new name: {name_validation['error']}"
                })
            validated_name = name_validation["cleaned_name"]
        
        # Validate new type if provided
        validated_type = None
        if new_type is not None and new_type.strip() != "":
            type_validation = validate_column_type(new_type)
            if not type_validation["valid"]:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid new type: {type_validation['error']}"
                })
            validated_type = type_validation["cleaned_type"]
        
        # Validate dropdown options if provided
        if dropdown_options is not None and len(dropdown_options) > 0:
            if not isinstance(dropdown_options, list):
                return compact_json_response({
                    "success": False,
                    "message": "Dropdown options must be a list."
                })
            
            if validated_type != "DROPDOWN":
                return compact_json_response({
                    "success": False,
                    "message": "Dropdown options can only be set when changing column type to DROPDOWN."
                })
        
        # Prepare the update data
        update_data = {
            "column_name": column_name.strip(),
            "new_name": validated_name,
            "new_type": validated_type,
            "dropdown_options": dropdown_options
        }
        
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
        
        # Validate that the column exists in the table
        existing_column_names: List[str] = [col.get("name", "") for col in columns]
        
        if update_data["column_name"] not in existing_column_names:
            return compact_json_response({
                "success": False,
                "message": f"Column '{update_data['column_name']}' not found in table."
            })
        
        # Create batch update requests
        requests = []
        
        # Convert existing columns to API format and apply updates
        updated_column_properties: List[Dict[str, Union[int, str, Dict]]] = []
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "TEXT")
            col_index = col.get("index", 0)
            
            # Check if this is the column being updated
            is_target_column = col_name == update_data["column_name"]
            
            # Create API format column property - only update the target column
            api_col_prop: Dict[str, Union[int, str, Dict]] = {
                "columnIndex": col_index,
                "columnName": col_name,  # Keep existing name by default
                "columnType": map_column_type(col_type)  # Keep existing type by default
            }
            
            # Only update the target column's properties
            if is_target_column:
                if update_data.get("new_name"):
                    api_col_prop["columnName"] = update_data["new_name"]
                if update_data.get("new_type"):
                    api_col_prop["columnType"] = map_column_type(update_data["new_type"])
                if update_data.get("dropdown_options") and len(update_data["dropdown_options"]) > 0:
                    api_col_prop["dataValidationRule"] = {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": option} for option in update_data["dropdown_options"]]
                        }
                    }
            elif "dataValidationRule" in col:
                # Preserve existing data validation for non-target columns
                api_col_prop["dataValidationRule"] = col["dataValidationRule"]
            
            updated_column_properties.append(api_col_prop)
        
        # Update table with new column properties
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "columnProperties": updated_column_properties
                },
                "fields": "columnProperties"
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
        
        # Prepare detailed response
        update_summary: Dict[str, Union[str, List[str]]] = {"column": update_data["column_name"]}
        if update_data.get("new_name"):
            update_summary["name_changed"] = update_data["new_name"]
        if update_data.get("new_type"):
            update_summary["type_changed"] = update_data["new_type"]
        if update_data.get("dropdown_options"):
            update_summary["dropdown_options"] = update_data["dropdown_options"]
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "column_updated": update_data["column_name"],
            "update_summary": update_summary,
            "message": f"Successfully updated column '{update_data['column_name']}' in table '{table_name}' in '{sheet_name}'"
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
            "message": f"Error managing column properties: {str(e)}"
        }) 