"""Handler for creating tables in Google Sheets."""

from typing import List, Dict, Any, Union, Optional
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    validate_table_name,
    validate_column_name,
    validate_column_type,
    check_duplicate_table_name,
    parse_cell_reference,
    map_column_type,
    get_number_format_for_type,
    get_table_ids_by_names,
    get_table_info
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def create_table_api(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_names: List[str],
    column_types: List[str],
    dropdown_columns: List[str],
    dropdown_values: List[str],
    start_position: str
) -> Dict[str, Any]:
    """
    API function for creating tables with column properties in a single call.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to create table in
        table_name: Name for the table
        column_names: List of column names
        column_types: List of column types
        dropdown_columns: List of column names that should have dropdown validation
        dropdown_values: List of comma-separated dropdown options for each dropdown column
        start_position: Starting position for the table (e.g., "A1", "B3")
    
    Returns:
        Dict: API response with success status and table details
    """
    try:
        # Validate table name
        table_validation = validate_table_name(table_name)
        if not table_validation["valid"]:
            return {
                "success": False,
                "message": table_validation["error"]
            }
        
        validated_table_name = table_validation["cleaned_name"]
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return {
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            }
        
        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return {
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
            }
        
        # Parse start position and calculate table range
        try:
            start_row, start_col = parse_cell_reference(start_position)
        except ValueError as e:
            return {
                "success": False,
                "message": f"Invalid start position '{start_position}': {str(e)}"
            }
        
        end_row = start_row + 1  # Header row
        end_col = start_col + len(column_names)
        
        # Create column properties
        column_properties = []
        for i, (col_name, col_type) in enumerate(zip(column_names, column_types)):
            column_property = {
                "columnIndex": i,
                "columnName": col_name,
                "columnType": map_column_type(col_type)
            }
            
            # Add data validation for dropdown columns
            if col_name in dropdown_columns:
                col_index = dropdown_columns.index(col_name)
                if col_index < len(dropdown_values):
                    options_str = dropdown_values[col_index]
                    options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
                    if options:
                        column_property["dataValidationRule"] = {
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [{"userEnteredValue": opt} for opt in options]
                            }
                        }
            
            column_properties.append(column_property)
        
        # Create unique table ID
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        table_id = f"table_{validated_table_name.lower().replace(' ', '_')}_{unique_id}"
        
        # Create addTable request with column properties
        add_table_request = {
            "addTable": {
                "table": {
                    "name": validated_table_name,
                    "tableId": table_id,
                    "range": {
                        "sheetId": sheet_id,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row
                    }
                }
            }
        }
        
        # Execute the API request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [add_table_request]}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        if replies and "addTable" in replies[0]:
            new_table = replies[0]["addTable"]
            table_id = new_table.get("tableId")
            
            return {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": validated_table_name,
                "table_id": table_id,
                "start_position": start_position,
                "column_count": len(column_names),
                "columns": column_names,
                "column_types": column_types,
                "range": f"{start_position}:{chr(ord('A') + end_col - 1)}{end_row}",
                "message": f"Successfully created table '{validated_table_name}' with {len(column_names)} columns in '{sheet_name}'"
            }
        else:
            return {
                "success": False,
                "message": "Failed to create table - no response data from API"
            }
        
    except HttpError as error:
        return {
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating table: {str(e)}"
        }

def update_table_properties(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_updates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Update column properties of an existing table.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        column_updates: List of column updates, each containing:
            - column_index: Index of the column to update (0-based)
            - column_name: New name for the column (optional)
            - column_type: New type for the column (optional)
            - dropdown_options: List of dropdown options (optional, for DROPDOWN type)
    
    Returns:
        Dict: API response with success status and update details
    """
    try:
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return {
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            }
        
        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return {
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
            }
        
        # Get table ID
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [table_name])
        table_id = table_ids.get(table_name)
        if not table_id:
            return {
                "success": False,
                "message": f"Table '{table_name}' not found in sheet '{sheet_name}'."
            }
        
        # Get current table information
        try:
            table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
            current_columns = table_info.get('columns', [])
        except Exception as e:
            return {
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            }
        
        # Create updated column properties
        updated_column_properties = []
        for i, col in enumerate(current_columns):
            col_name = col.get("name", f"Column {i+1}")
            col_type = col.get("type", "TEXT")
            col_index = col.get("index", i)
            
            # Create base column property
            column_property = {
                "columnIndex": col_index,
                "columnName": col_name,
                "columnType": map_column_type(col_type)
            }
            
            # Check if this column needs to be updated
            for update in column_updates:
                if update.get("column_index") == i:
                    # Update column name if provided
                    if "column_name" in update and update["column_name"]:
                        name_validation = validate_column_name(update["column_name"])
                        if not name_validation["valid"]:
                            return {
                                "success": False,
                                "message": f"Invalid column name: {name_validation['error']}"
                            }
                        column_property["columnName"] = name_validation["cleaned_name"]
                    
                    # Update column type if provided
                    if "column_type" in update and update["column_type"]:
                        type_validation = validate_column_type(update["column_type"])
                        if not type_validation["valid"]:
                            return {
                                "success": False,
                                "message": f"Invalid column type: {type_validation['error']}"
                            }
                        column_property["columnType"] = map_column_type(type_validation["cleaned_type"])
                    
                    # Add dropdown validation if provided
                    if "dropdown_options" in update and update["dropdown_options"]:
                        if not isinstance(update["dropdown_options"], list):
                            return {
                                "success": False,
                                "message": "Dropdown options must be a list."
                            }
                        
                        if len(update["dropdown_options"]) > 0:
                            column_property["dataValidationRule"] = {
                                "condition": {
                                    "type": "ONE_OF_LIST",
                                    "values": [{"userEnteredValue": opt} for opt in update["dropdown_options"]]
                                }
                            }
                    
                    break
            
            # Preserve existing data validation if not being updated
            if "dataValidationRule" in col and "dataValidationRule" not in column_property:
                column_property["dataValidationRule"] = col["dataValidationRule"]
            
            updated_column_properties.append(column_property)
        
        # Create update request
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "columnProperties": updated_column_properties
                },
                "fields": "columnProperties"
            }
        }
        
        # Execute the API request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [update_table_request]}
        ).execute()
        
        # Prepare response
        update_summary = []
        for update in column_updates:
            col_index = update.get("column_index")
            summary = {"column_index": col_index}
            
            if "column_name" in update:
                summary["name_changed"] = update["column_name"]
            if "column_type" in update:
                summary["type_changed"] = update["column_type"]
            if "dropdown_options" in update:
                summary["dropdown_options"] = update["dropdown_options"]
            
            update_summary.append(summary)
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": table_id,
            "updates_applied": update_summary,
            "message": f"Successfully updated {len(column_updates)} column(s) in table '{table_name}'"
        }
        
    except HttpError as error:
        return {
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating table properties: {str(e)}"
        }



def create_table_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    start_cell: str,
    column_names: List[str],
    column_types: List[str],
    dropdown_columns: List[str] = [],
    dropdown_values: List[str] = []
) -> str:
    """
    Create a new table in Google Sheets using the official addTable operation.
    
    Available column types:
    - TEXT: Plain text data
    - DOUBLE: Numeric data with decimals
    - CURRENCY: Monetary values ($#,##0.00)
    - PERCENT: Percentage values (0.00%)
    - DATE: Date values (yyyy-mm-dd)
    - TIME: Time values (hh:mm:ss)
    - DATE_TIME: Date and time values
    - BOOLEAN: True/false values
    - DROPDOWN: Selection from predefined options
    - COLUMN_TYPE_UNSPECIFIED: Defaults to TEXT
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to create table in
        table_name: Name for the table
        start_cell: Starting cell for the table (e.g., "A1")
        column_names: List of column names
        column_types: List of column types corresponding to column_names
        dropdown_columns: List of column names that should have dropdown validation
        dropdown_values: List of comma-separated dropdown options for each dropdown column
    
    Returns:
        str: Success message with table details
    """
    try:
        # Create table with column properties in a single API call
        create_result = create_table_api(
            drive_service=drive_service,
            sheets_service=sheets_service,
            spreadsheet_name=spreadsheet_name,
            sheet_name=sheet_name,
            table_name=table_name,
            column_names=column_names,
            column_types=column_types,
            dropdown_columns=dropdown_columns,
            dropdown_values=dropdown_values,
            start_position=start_cell
        )

        # Check if table creation was successful
        if not create_result["success"]:
            return compact_json_response(create_result)

        # Step 2: Update table properties using update_table_properties function
        # Create column updates based on the provided column names and types
        column_updates = []
        for i, (col_name, col_type) in enumerate(zip(column_names, column_types)):
            update = {
                "column_index": i,
                "column_name": col_name,
                "column_type": col_type
            }
            
            # Add dropdown options if this column is in dropdown_columns
            if col_name in dropdown_columns:
                col_index = dropdown_columns.index(col_name)
                if col_index < len(dropdown_values):
                    options_str = dropdown_values[col_index]
                    options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
                    if options:
                        update["dropdown_options"] = options
            
            column_updates.append(update)
        
        # Call update_table_properties to set the column properties
        update_result = update_table_properties(
            drive_service=drive_service,
            sheets_service=sheets_service,
            spreadsheet_name=spreadsheet_name,
            sheet_name=sheet_name,
            table_name=table_name,
            column_updates=column_updates
        )
        
        # Check if update was successful
        if not update_result["success"]:
            return compact_json_response(update_result)
        
        # Combine results
        final_result = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": create_result.get("table_id"),
            "start_cell": start_cell,
            "column_count": len(column_names),
            "columns": column_names,
            "column_types": column_types,
            "range": create_result.get("range"),
            "dropdown_columns": dropdown_columns,
            "updates_applied": update_result.get("updates_applied", []),
            "message": f"Successfully created and updated table '{table_name}' with {len(column_names)} columns in '{sheet_name}'"
        }
        
        return compact_json_response(final_result)
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error creating table: {str(e)}"
        }) 