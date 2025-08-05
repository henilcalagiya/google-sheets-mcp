"""Handler for creating tables in Google Sheets."""

from typing import List, Dict, Any, Union
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    validate_table_name,
    validate_column_name,
    validate_column_type,
    check_duplicate_table_name,
    parse_cell_reference,
    map_column_type
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

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
        # Validate table name
        table_validation = validate_table_name(table_name)
        if not table_validation["valid"]:
            return compact_json_response({
                "success": False,
                "message": table_validation["error"]
            })
        
        validated_table_name = table_validation["cleaned_name"]
        
        # Validate inputs
        if not column_names or len(column_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one column name is required."
            })
        
        if not column_types or len(column_types) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one column type is required."
            })
        
        if len(column_names) != len(column_types):
            return compact_json_response({
                "success": False,
                "message": f"Number of column names ({len(column_names)}) must match number of column types ({len(column_types)})."
            })
        
        # Validate start cell
        if not start_cell or start_cell.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Start cell is required (e.g., 'A1')."
            })
        
        # Validate dropdown parameters
        if len(dropdown_columns) != len(dropdown_values):
            return compact_json_response({
                "success": False,
                "message": f"Number of dropdown columns ({len(dropdown_columns)}) must match number of dropdown values ({len(dropdown_values)})."
            })
        
        # Validate column names and types
        validated_column_names = []
        validated_column_types = []
        invalid_columns = []
        
        for i, (col_name, col_type) in enumerate(zip(column_names, column_types)):
            # Validate column name
            col_name_validation = validate_column_name(col_name)
            if not col_name_validation["valid"]:
                invalid_columns.append({"index": i, "name": col_name, "error": col_name_validation["error"]})
                continue
            
            # Validate column type
            col_type_validation = validate_column_type(col_type)
            if not col_type_validation["valid"]:
                invalid_columns.append({"index": i, "name": col_name, "error": col_type_validation["error"]})
                continue
            
            validated_column_names.append(col_name_validation["cleaned_name"])
            validated_column_types.append(col_type_validation["cleaned_type"])
        
        if invalid_columns:
            error_messages = [f"Column {item['index']+1} '{item['name']}': {item['error']}" for item in invalid_columns]
            return compact_json_response({
                "success": False,
                "message": f"Invalid columns: {'; '.join(error_messages)}",
                "invalid_columns": invalid_columns
            })
        
        if not validated_column_names:
            return compact_json_response({
                "success": False,
                "message": "No valid columns provided after validation."
            })
        
        # Check for duplicate column names
        seen_names = set()
        duplicate_columns = []
        for col_name in validated_column_names:
            if col_name in seen_names:
                duplicate_columns.append(col_name)
            else:
                seen_names.add(col_name)
        
        if duplicate_columns:
            return compact_json_response({
                "success": False,
                "message": f"Duplicate column names found: {', '.join(duplicate_columns)}"
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
        
        # Check for duplicate table name
        duplicate_check = check_duplicate_table_name(sheets_service, spreadsheet_id, sheet_name, validated_table_name)
        if duplicate_check["has_duplicate"]:
            return compact_json_response({
                "success": False,
                "message": duplicate_check["error"]
            })
        
        # Create a mapping of column names to their dropdown options
        dropdown_mapping = {}
        for col_name, options_str in zip(dropdown_columns, dropdown_values):
            if col_name not in validated_column_names:
                return compact_json_response({
                    "success": False,
                    "message": f"Dropdown column '{col_name}' not found in column_names."
                })
            options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
            dropdown_mapping[col_name] = options
        
        # Calculate table range
        try:
            start_row, start_col = parse_cell_reference(start_cell)
        except ValueError as e:
            return compact_json_response({
                "success": False,
                "message": f"Invalid start cell '{start_cell}': {str(e)}"
            })
        
        end_row = start_row + 1  # Header row
        end_col = start_col + len(validated_column_names)
        
        # Build column properties according to official API documentation
        column_properties = []
        for i, (col_name, col_type) in enumerate(zip(validated_column_names, validated_column_types)):
            column_property = {
                "columnIndex": i,
                "columnName": col_name,
                "columnType": map_column_type(col_type)
            }
            
            # Add data validation for dropdown columns
            if col_name in dropdown_mapping:
                options = dropdown_mapping[col_name]
                if options:
                    column_property["dataValidationRule"] = {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": opt} for opt in options]
                        }
                    }
            
            column_properties.append(column_property)
        
        # Create addTable request according to official API documentation
        add_table_request = {
            "addTable": {
                "table": {
                    "name": validated_table_name,
                    "tableId": f"table_{validated_table_name.lower().replace(' ', '_')}",
                    "range": {
                        "sheetId": sheet_id,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row
                    },
                    "columnProperties": column_properties
                }
            }
        }
        
        # Execute the addTable request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [add_table_request]}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        if replies and "addTable" in replies[0]:
            new_table = replies[0]["addTable"]
            table_id = new_table.get("tableId")
            
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": validated_table_name,
                "table_id": table_id,
                "start_cell": start_cell,
                "column_count": len(validated_column_names),
                "columns": validated_column_names,
                "column_types": validated_column_types,
                "range": f"{start_cell}:{chr(ord('A') + end_col - 1)}{end_row}",
                "dropdown_columns": list(dropdown_mapping.keys()),
                "message": f"Successfully created table '{validated_table_name}' with {len(validated_column_names)} columns in '{sheet_name}'"
            }
            
            # Add warning if there was a warning during duplicate check
            if "warning" in duplicate_check:
                response_data["warning"] = duplicate_check["warning"]
            
            return compact_json_response(response_data)
        else:
            return compact_json_response({
                "success": False,
                "message": "Failed to create table - no response data from API"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error creating table: {str(e)}"
        }) 