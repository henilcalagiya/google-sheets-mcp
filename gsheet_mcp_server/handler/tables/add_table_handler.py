"""Handler for adding tables to Google Sheets."""

from typing import List
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.json_utils import compact_json_response

def add_table_handler(
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
    Add a table to a Google Spreadsheet.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to add table to
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
        if not table_name or table_name.strip() == "":
            return "❌ Error: Table name is required and cannot be empty."
        
        # Clean and validate table name
        table_name = _clean_table_name(table_name)
        if not table_name:
            return "❌ Error: Invalid table name. Please provide a valid name."
        
        # Validate inputs
        if not column_names or len(column_names) == 0:
            return "❌ Error: At least one column name is required."
        
        if not column_types or len(column_types) == 0:
            return "❌ Error: At least one column type is required."
        
        if len(column_names) != len(column_types):
            return f"❌ Error: Number of column names ({len(column_names)}) must match number of column types ({len(column_types)})."
        

        
        # Validate dropdown parameters
        if len(dropdown_columns) != len(dropdown_values):
            return f"❌ Error: Number of dropdown columns ({len(dropdown_columns)}) must match number of dropdown values ({len(dropdown_values)})."
        
        # Create a mapping of column names to their dropdown options
        dropdown_mapping = {}
        for col_name, options_str in zip(dropdown_columns, dropdown_values):
            if col_name not in column_names:
                return f"❌ Error: Dropdown column '{col_name}' not found in column_names."
            options = [opt.strip() for opt in options_str.split(",")]
            dropdown_mapping[col_name] = options
        
        # Build column properties from separated parameters
        processed_column_properties = []
        
        for i, (col_name, col_type) in enumerate(zip(column_names, column_types)):
            # Validate column name
            if not col_name or col_name.strip() == "":
                return f"❌ Error: Column {i} must have a valid name."
            
            # Validate column type
            valid_types = ["TEXT", "NUMBER", "DATE", "TIME", "DATE_TIME", "BOOLEAN", "PERCENT", "CURRENCY", "DROPDOWN", "NONE"]
            if col_type not in valid_types:
                return f"❌ Error: Column '{col_name}' has invalid type '{col_type}'. Valid types: {', '.join(valid_types)}"
            
            # Map user-friendly types to Google Sheets API types
            api_type_mapping = {
                "TEXT": "TEXT",
                "NUMBER": "DOUBLE",  # Google Sheets API uses DOUBLE for numbers
                "DATE": "DATE",
                "TIME": "TIME",
                "DATE_TIME": "DATE_TIME",
                "BOOLEAN": "BOOLEAN",
                "PERCENT": "PERCENT",
                "CURRENCY": "CURRENCY",
                "DROPDOWN": "DROPDOWN",
                "NONE": "COLUMN_TYPE_UNSPECIFIED"  # Google Sheets API unspecified type
            }
            
            # Convert to API type
            api_column_type = api_type_mapping.get(col_type, "TEXT")
            
            # Create column property
            column_prop = {
                "columnIndex": i,
                "columnName": col_name.strip(),
                "columnType": api_column_type
            }
            
            # Add dropdown validation if this column is in dropdown_columns
            if col_name in dropdown_mapping:
                options = dropdown_mapping[col_name]
                column_prop["dataValidationRule"] = {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": opt} for opt in options]
                    }
                }
                # Convert to DROPDOWN type if it was TEXT
                if col_type == "TEXT":
                    column_prop["columnType"] = "DROPDOWN"
                elif col_type == "NUMBER":
                    column_prop["columnType"] = "DOUBLE"
            
            processed_column_properties.append(column_prop)

        # Use utility functions to get spreadsheet and sheet IDs
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return f"❌ Error: Spreadsheet '{spreadsheet_name}' not found."

        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return f"❌ Error: Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."

        # Create table request with proper structure
        table_request = {
            "addTable": {
                "table": {
                    "name": table_name,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": _get_row_index(start_cell),
                        "endRowIndex": _get_row_index(start_cell) + 1,  # Header row only
                        "startColumnIndex": _get_column_index(start_cell),
                        "endColumnIndex": _get_column_index(start_cell) + len(column_names)
                    },
                    "columnProperties": processed_column_properties
                }
            }
        }
        
        # Add header data with proper data types
        header_values = []
        for i, column_prop in enumerate(processed_column_properties):
            col_name = column_prop["columnName"]
            col_type = column_prop["columnType"]
            
            # Create cell value based on column type
            if col_type == "NUMBER":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "DATE":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "TIME":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "DATE_TIME":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "BOOLEAN":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "PERCENT":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "CURRENCY":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "DROPDOWN":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            elif col_type == "NONE":
                cell_value = {"userEnteredValue": {"stringValue": col_name}}  # Header as text
            else:  # TEXT or default
                cell_value = {"userEnteredValue": {"stringValue": col_name}}
            
            header_values.append(cell_value)
        
        header_request = {
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": _get_row_index(start_cell),
                    "endRowIndex": _get_row_index(start_cell) + 1,
                    "startColumnIndex": _get_column_index(start_cell),
                    "endColumnIndex": _get_column_index(start_cell) + len(column_names)
                },
                "rows": [{"values": header_values}],
                "fields": "userEnteredValue"
            }
        }
        

        

        
        # Set number formats for different column types
        format_requests = []
        for i, column_prop in enumerate(processed_column_properties):
            col_type = column_prop["columnType"]
            col_index = _get_column_index(start_cell) + i
            
            if col_type in ["PERCENT", "CURRENCY", "NUMBER", "TIME", "DATE_TIME"]:
                format_request = {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": _get_row_index(start_cell) + 1,  # Data rows (skip header)
                            "endRowIndex": _get_row_index(start_cell) + 100,  # Apply to 100 rows
                            "startColumnIndex": col_index,
                            "endColumnIndex": col_index + 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": _get_number_format(col_type)
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat"
                    }
                }
                format_requests.append(format_request)
        
        # Prepare batch update request
        requests = [table_request, header_request] + format_requests
        
        batch_request = {
            "requests": requests
        }
        
        # Execute batch update
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_request
        ).execute()
        
        return compact_json_response({
            "success": True,
            "message": f"Successfully created table '{table_name}' in sheet '{sheet_name}' starting at {start_cell} with {len(column_names)} columns: {', '.join(column_names)}",
            "data": {
                "table_name": table_name,
                "sheet_name": sheet_name,
                "start_cell": start_cell,
                "column_count": len(column_names),
                "column_names": column_names
            }
        })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Error creating table: {error}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        })


def _calculate_table_range(start_cell: str, num_columns: int) -> str:
    """Calculate table range based on start cell and number of columns."""
    import re
    
    # Parse start cell (e.g., "A1")
    match = re.match(r'([A-Z]+)(\d+)', start_cell.upper())
    if not match:
        raise ValueError(f"Invalid start cell format: {start_cell}")
    
    start_col = match.group(1)
    start_row = int(match.group(2))
    
    # Calculate end column
    end_col = _get_column_letter(_get_column_index(start_cell) + num_columns - 1)
    
    return f"{start_cell}:{end_col}{start_row}"


def _get_row_index(cell: str) -> int:
    """Get row index from cell reference (0-based)."""
    import re
    match = re.match(r'[A-Z]+(\d+)', cell.upper())
    if match:
        return int(match.group(1)) - 1
    return 0


def _get_column_index(cell: str) -> int:
    """Get column index from cell reference (0-based)."""
    import re
    match = re.match(r'([A-Z]+)\d+', cell.upper())
    if match:
        col_str = match.group(1)
        result = 0
        for char in col_str:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1
    return 0


def _get_column_letter(column_index: int) -> str:
    """Convert column index to letter (e.g., 0 -> A, 25 -> Z, 26 -> AA)."""
    result = ""
    while column_index >= 0:
        column_index, remainder = divmod(column_index, 26)
        result = chr(65 + remainder) + result
        column_index -= 1
    return result


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


def _map_column_type(col_type: str) -> str:
    """
    Map user-friendly column types to Google Sheets API column types.
    
    Args:
        col_type: User-friendly column type (e.g., "text", "number", "date")
        
    Returns:
        str: Google Sheets API column type
    """
    col_type = col_type.lower()
    
    type_mapping = {
        "text": "TEXT",
        "string": "TEXT",
        "number": "NUMBER",
        "numeric": "NUMBER",
        "date": "DATE",
        "datetime": "DATE_TIME",
        "time": "TIME_OF_DAY",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "dropdown": "TEXT",  # Dropdowns are text with validation
        "select": "TEXT",
        "percent": "PERCENT",
        "currency": "CURRENCY"
    }
    
    return type_mapping.get(col_type, "TEXT")


def _clean_table_name(table_name: str) -> str:
    """
    Clean and validate table name for Google Sheets.
    
    Args:
        table_name: Raw table name from user
        
    Returns:
        str: Cleaned table name or empty string if invalid
    """
    import re
    
    if not table_name:
        return ""
    
    # Remove leading/trailing whitespace
    table_name = table_name.strip()
    
    if not table_name:
        return ""
    
    # Remove invalid characters (only allow letters, numbers, spaces, hyphens, underscores)
    # Replace invalid characters with spaces
    table_name = re.sub(r'[^a-zA-Z0-9\s\-_]', ' ', table_name)
    
    # Replace multiple spaces with single space
    table_name = re.sub(r'\s+', ' ', table_name)
    
    # Remove leading/trailing spaces again
    table_name = table_name.strip()
    
    # Ensure it starts with a letter or number
    if not re.match(r'^[a-zA-Z0-9]', table_name):
        return ""
    
    # Limit length to 50 characters
    if len(table_name) > 50:
        table_name = table_name[:50].strip()
    
    # If it's just "table" or similar generic names, make it more descriptive
    if table_name.lower() in ['table', 'new table', 'untitled']:
        table_name = f"Table"
    
    return table_name 