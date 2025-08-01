"""Handler for adding columns to existing tables in Google Sheets."""

from typing import List, Any, Dict
from googleapiclient.errors import HttpError
import re
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import get_table_ids_by_names, get_table_info
from gsheet_mcp_server.helper.json_utils import compact_json_response


def add_table_column_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_names: List[str],
    column_types: List[str],
    positions: List[int] = None,
    dropdown_columns: List[str] = [],
    dropdown_values: List[str] = []
) -> str:
    """
    Add new columns to an existing table in Google Sheets.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add columns to
        column_names: List of names for the new columns
        column_types: List of types for the new columns (TEXT, NUMBER, DATE, etc.)
        positions: List of positions to insert columns (0-based, None for end)
        dropdown_columns: List of column names that should have dropdown validation
        dropdown_values: List of comma-separated dropdown options for each dropdown column
    
    Returns:
        str: Success message with column details
    """
    try:
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
        
        # Validate dropdown parameters
        if len(dropdown_columns) != len(dropdown_values):
            return compact_json_response({
                "success": False,
                "message": f"Number of dropdown columns ({len(dropdown_columns)}) must match number of dropdown values ({len(dropdown_values)})."
            })
        
        # Create a mapping of column names to their dropdown options
        dropdown_mapping = {}
        for col_name, options_str in zip(dropdown_columns, dropdown_values):
            if col_name not in column_names:
                return compact_json_response({
                    "success": False,
                    "message": f"Dropdown column '{col_name}' not found in column_names."
                })
            options = [opt.strip() for opt in options_str.split(",")]
            dropdown_mapping[col_name] = options
        
        # Clean and validate column names
        cleaned_column_names = []
        for i, col_name in enumerate(column_names):
            if not col_name or col_name.strip() == "":
                return compact_json_response({
                    "success": False,
                    "message": f"Column {i} name is required and cannot be empty."
                })
            
            cleaned_name = _clean_column_name(col_name)
            if not cleaned_name:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid column name '{col_name}'. Please provide a valid name."
                })
            cleaned_column_names.append(cleaned_name)
        
        # Validate column types
        valid_types = ["TEXT", "NUMBER", "DATE", "TIME", "DATE_TIME", "BOOLEAN", "PERCENT", "CURRENCY", "DROPDOWN", "NONE"]
        for i, col_type in enumerate(column_types):
            if col_type not in valid_types:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid column type '{col_type}' for column '{column_names[i]}'. Valid types: {', '.join(valid_types)}"
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
        except RuntimeError as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        # Determine insert positions
        insert_positions = []
        if positions is None:
            # Add all columns at the end
            for i in range(len(column_names)):
                insert_positions.append(current_column_count + i)
        else:
            if len(positions) != len(column_names):
                return compact_json_response({
                    "success": False,
                    "message": f"Number of positions ({len(positions)}) must match number of columns ({len(column_names)})."
                })
            
            for i, position in enumerate(positions):
                if position < 0 or position > current_column_count + i:
                    return compact_json_response({
                        "success": False,
                        "message": f"Invalid position {position} for column '{column_names[i]}'. Must be between 0 and {current_column_count + i}."
                    })
                insert_positions.append(position)
        
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
        
        # Get sheet ID for insert dimension operation
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        
        # Calculate the actual column positions in the sheet
        table_start_col = table_info.get('start_col', 0)
        table_start_row = table_info.get('start_row', 0)
        
        # Prepare batch update requests
        requests = []
        added_columns = []
        
        # First, expand the table range to accommodate new columns
        # This ensures the table can hold the new columns without affecting other tables
        total_new_columns = len(column_names)
        new_table_end_col = table_info.get('end_col', 0) + total_new_columns
        
        # Update table range to include space for new columns
        update_table_range_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_start_row,
                        "endRowIndex": table_info.get('end_row', 0),
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": new_table_end_col
                    }
                },
                "fields": "range"
            }
        }
        requests.append(update_table_range_request)
        
        # Execute the range update first to ensure the table is expanded
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [update_table_range_request]}
        ).execute()
        
        # Sort positions in descending order to avoid shifting issues
        sorted_positions = sorted(insert_positions, reverse=True)
        
        for i, (col_name, col_type, position) in enumerate(zip(cleaned_column_names, column_types, insert_positions)):
            # Calculate the actual column position in the sheet
            sheet_column_position = table_start_col + position
            
            # Step 2: Update the table to include the new column properties
            api_column_type = api_type_mapping.get(col_type, "TEXT")
            new_column_property = {
                "columnIndex": position,
                "columnName": col_name,
                "columnType": api_column_type
            }
            
            # Add dropdown validation if specified
            if col_name in dropdown_mapping:
                new_column_property["dataValidationRule"] = {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": opt} for opt in dropdown_mapping[col_name]]
                    }
                }
                # Ensure column type is DROPDOWN if validation is specified
                if col_type == "TEXT":
                    new_column_property["columnType"] = "DROPDOWN"
            
            # Update table properties to include the new column
            update_table_request = {
                "updateTable": {
                    "table": {
                        "tableId": table_id,
                        "columnProperties": [new_column_property]
                    },
                    "fields": "columnProperties"
                }
            }
            requests.append(update_table_request)
            
            # Step 3: Update the header cell with the column name
            header_update_request = {
                "updateCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_start_row,
                        "endRowIndex": table_start_row + 1,
                        "startColumnIndex": sheet_column_position,
                        "endColumnIndex": sheet_column_position + 1
                    },
                    "rows": [{"values": [{"userEnteredValue": {"stringValue": col_name}}]}],
                    "fields": "userEnteredValue"
                }
            }
            requests.append(header_update_request)
            
            added_columns.append({
                "name": col_name,
                "type": col_type,
                "position": position
            })
        
        # Prepare batch update request with remaining operations (excluding range update)
        remaining_requests = [req for req in requests if req != update_table_range_request]
        batch_request = {
            "requests": remaining_requests
        }
        
        # Execute batch update for column properties and headers
        if remaining_requests:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=batch_request
            ).execute()
        
        # Prepare response message
        if len(added_columns) == 1:
            col = added_columns[0]
            position_text = f"at position {col['position']}" if positions else "at the end"
            message = f"Successfully added column '{col['name']}' ({col['type']}) to table '{table_name}' {position_text} in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        else:
            position_text = "at specified positions" if positions else "at the end"
            message = f"Successfully added {len(added_columns)} columns to table '{table_name}' {position_text} in sheet '{sheet_name}' of spreadsheet '{spreadsheet_name}'."
        
        return compact_json_response({
            "success": True,
            "message": message,
            "data": {
                "added_columns": added_columns,
                "table_name": table_name,
                "sheet_name": sheet_name,
                "spreadsheet_name": spreadsheet_name,
                "total_added": len(added_columns)
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error adding table column: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        })


def _clean_column_name(column_name: str) -> str:
    """
    Clean and validate column name for Google Sheets.
    
    Args:
        column_name: Raw column name from user
        
    Returns:
        str: Cleaned column name or empty string if invalid
    """
    if not column_name:
        return ""
    
    # Remove leading/trailing whitespace
    column_name = column_name.strip()
    
    if not column_name:
        return ""
    
    # Remove invalid characters (only allow letters, numbers, spaces, hyphens, underscores)
    column_name = re.sub(r'[^a-zA-Z0-9\s\-_]', ' ', column_name)
    
    # Replace multiple spaces with single space
    column_name = re.sub(r'\s+', ' ', column_name)
    
    # Remove leading/trailing spaces again
    column_name = column_name.strip()
    
    # Ensure it starts with a letter or number
    if not re.match(r'^[a-zA-Z0-9]', column_name):
        return ""
    
    # Limit length to 50 characters
    if len(column_name) > 50:
        column_name = column_name[:50].strip()
    
    return column_name


def _get_number_format(col_type: str) -> dict:
    """
    Get number format for different column types.
    
    Args:
        col_type: Google Sheets API column type
        
    Returns:
        dict: Number format specification
    """
    if col_type == "PERCENT":
        return {"type": "PERCENT", "pattern": "0.00%"}
    elif col_type == "CURRENCY":
        return {"type": "CURRENCY", "pattern": "$#,##0.00"}
    elif col_type == "NUMBER":
        return {"type": "NUMBER", "pattern": "#,##0.00"}
    elif col_type == "TIME":
        return {"type": "TIME", "pattern": "hh:mm:ss"}
    elif col_type == "DATE_TIME":
        return {"type": "DATE_TIME", "pattern": "yyyy-mm-dd hh:mm:ss"}
    else:
        return {"type": "TEXT"} 