"""Handler for adding columns to tables in Google Sheets."""

from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    validate_column_name,
    validate_column_type,
    get_table_ids_by_names,
    get_table_info,
    map_column_type,
    get_number_format_for_type
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def add_table_column_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_names: List[str],
    column_types: List[str],
    positions: List[int] = [],
    dropdown_columns: List[str] = [],
    dropdown_values: List[str] = []
) -> str:
    """
    Add new columns to an existing table in Google Sheets.
    
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
    
    According to the official Google Sheets API documentation, to add columns to a table:
    1. Use InsertRangeRequest to insert new columns in the sheet (API handles position shifting)
    2. Use UpdateTableRequest to update the table range and column properties
    
    The table will automatically recognize the new columns with proper types and validation.
    The Google Sheets API automatically handles position shifting for existing columns.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add columns to
        column_names: List of column names to add
        column_types: List of column types corresponding to column_names
        positions: List of positions to insert columns (0-based index, empty list for end)
        dropdown_columns: List of column names that should have dropdown validation
        dropdown_values: List of comma-separated dropdown options strings
    
    Returns:
        str: Success message with column addition details
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
                "message": "Column name is required."
            })
        
        if not column_types or len(column_types) == 0:
            return compact_json_response({
                "success": False,
                "message": "Column type is required."
            })
        
        # Validate input lengths match
        if len(column_names) != len(column_types):
            return compact_json_response({
                "success": False,
                "message": f"Number of column names ({len(column_names)}) must match number of column types ({len(column_types)})."
            })
        
        # Validate positions if provided
        if positions and len(positions) != len(column_names):
            return compact_json_response({
                "success": False,
                "message": f"Number of positions ({len(positions)}) must match number of columns ({len(column_names)})."
            })
        
        # Validate position values are non-negative
        if positions:
            invalid_positions = [pos for pos in positions if pos < 0]
            if invalid_positions:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid positions found: {invalid_positions}. Positions must be 0-based non-negative integers."
                })
        
        # Validate dropdown parameters
        if dropdown_columns and dropdown_values:
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
            error_messages = [f"Column {item['index']} '{item['name']}': {item['error']}" for item in invalid_columns]
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
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve table information: {str(e)}"
            })
        
        # Check for conflicts with existing column names
        existing_column_names = [col.get("name", "") for col in table_info.get("columns", [])]
        conflicting_columns = []
        for col_name in validated_column_names:
            if col_name in existing_column_names:
                conflicting_columns.append(col_name)
        
        if conflicting_columns:
            return compact_json_response({
                "success": False,
                "message": f"Column names already exist in table: {', '.join(conflicting_columns)}"
            })
        
        # Create a mapping of column names to their dropdown options
        dropdown_mapping = {}
        if dropdown_columns and dropdown_values:
            # Create mapping by matching column names
            for col_name, options_str in zip(dropdown_columns, dropdown_values):
                if col_name not in validated_column_names:
                    return compact_json_response({
                        "success": False,
                        "message": f"Dropdown column '{col_name}' not found in column_names: {validated_column_names}."
                    })
                options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
                dropdown_mapping[col_name] = options
        
        # Get current table range
        current_range = table_info.get("range", {})
        current_start_col = current_range.get("startColumnIndex", 0)
        current_end_col = current_range.get("endColumnIndex", 0)
        current_start_row = current_range.get("startRowIndex", 0)
        current_end_row = current_range.get("endRowIndex", 0)
        
        # Get existing column objects for processing
        existing_columns = table_info.get("columns", [])
        
        # Calculate insertion positions
        if positions:
            # Use provided positions (0-based)
            insertion_positions = positions.copy()
            # Validate positions don't exceed current table column count
            # Allow positions up to the current column count (for inserting at the end)
            max_position = len(existing_columns)
            invalid_positions = [pos for pos in insertion_positions if pos > max_position]
            if invalid_positions:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid positions found: {invalid_positions}. Positions must be 0-based and not exceed current column count ({max_position})."
                })
            # Sort positions in descending order (rightmost to leftmost) for proper insertion
            insertion_positions.sort(reverse=True)
        else:
            # Insert at the end
            insertion_positions = [len(existing_columns)] * len(validated_column_names)
        
        # Create requests according to official API documentation
        requests = []
        
        # 1. Insert new columns using InsertRangeRequest (rightmost to leftmost)
        for pos in insertion_positions:
            # Ensure position is within valid range
            if pos < 0:
                pos = 0
            if pos > len(existing_columns):
                pos = len(existing_columns)

            insert_request = {
                "insertRange": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": current_end_row,
                        "startColumnIndex": pos,
                        "endColumnIndex": pos + 1
                    },
                    "shiftDimension": "COLUMNS"
                }
            }
            requests.append(insert_request)
        
        # 2. Build complete column properties array for UpdateTableRequest
        # Start with existing columns and their updated indices after insertions
        full_column_properties = []
        
        def create_column_property(col_name, col_type, col_index):
            """Helper function to create column property with dropdown validation."""
            column_property = {
                "columnIndex": col_index,
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
            
            return column_property
        
        # Create new column properties with their final positions
        new_column_properties = []
        for i, (col_name, col_type) in enumerate(zip(validated_column_names, validated_column_types)):
            if positions:
                # Use the original position for new columns (positions are already sorted)
                col_index = positions[i]
            else:
                # For end insertions, use the position after existing columns
                col_index = len(existing_columns) + i
            
            new_column_properties.append(create_column_property(col_name, col_type, col_index))
        
        # Build the complete column properties array
        # First, add existing columns with their updated indices
        existing_col_index = 0
        new_col_index = 0
        
        # Sort new columns by their target positions for proper insertion
        if positions:
            # Create pairs of (position, column_property) and sort by position
            new_cols_with_positions = list(zip(positions, new_column_properties))
            new_cols_with_positions.sort(key=lambda x: x[0])
            new_column_properties = [col_prop for _, col_prop in new_cols_with_positions]
            new_positions = [pos for pos, _ in new_cols_with_positions]
        else:
            new_positions = list(range(len(existing_columns), len(existing_columns) + len(validated_column_names)))
        
        # Convert existing columns back to API format and build the complete array
        api_existing_columns = []
        for col_info in existing_columns:
            api_col_prop = {
                "columnIndex": col_info.get("index", 0),
                "columnName": col_info.get("name", ""),
                "columnType": col_info.get("type", "TEXT")
            }
            # Preserve dataValidationRule if it exists
            if "dataValidationRule" in col_info:
                api_col_prop["dataValidationRule"] = col_info["dataValidationRule"]
            api_existing_columns.append(api_col_prop)
        
        # Build the complete array by inserting new columns at their positions
        full_column_properties = api_existing_columns.copy()
        
        # Insert new columns at their target positions (rightmost to leftmost to avoid index shifting)
        for i in range(len(new_column_properties) - 1, -1, -1):
            insert_pos = new_positions[i]
            col_prop = new_column_properties[i]
            # Update the column index to match the final position
            col_prop["columnIndex"] = insert_pos
            full_column_properties.insert(insert_pos, col_prop)
        
        # Update all existing column indices to reflect their new positions after insertions
        for i, col_prop in enumerate(full_column_properties):
            col_prop["columnIndex"] = i
        
        # Update table with complete column properties
        new_end_col = current_end_col + len(validated_column_names)
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": current_start_row,
                        "endRowIndex": current_end_row,
                        "startColumnIndex": current_start_col,
                        "endColumnIndex": new_end_col
                    },
                    "columnProperties": full_column_properties
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
        if replies:
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "added_columns": validated_column_names,
                "column_types": validated_column_types,
                "columns_added": len(validated_column_names),
                "new_column_count": len(existing_columns) + len(validated_column_names),
                "insertion_positions": positions if positions else ["end"] * len(validated_column_names),
                "message": f"Successfully added {len(validated_column_names)} column(s) to table '{table_name}' in '{sheet_name}'"
            }
            
            return compact_json_response(response_data)
        else:
            return compact_json_response({
                "success": False,
                "message": "Failed to add columns - no response data from API"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error adding table columns: {str(e)}"
        }) 