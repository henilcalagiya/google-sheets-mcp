"""Helper utilities for Google Sheets table operations."""

from typing import Dict, Any, Optional, List, Union, Tuple
from googleapiclient.errors import HttpError
import re

def validate_table_name(name: str) -> Dict[str, Any]:
    """
    Validate a table name according to Google Sheets rules.
    
    Args:
        name: Table name to validate
    
    Returns:
        Dictionary with validation result
    """
    if not name or name.strip() == "":
        return {"valid": False, "error": "Table name cannot be empty"}
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Check length (Google Sheets limit is 100 characters)
    if len(name) > 100:
        return {"valid": False, "error": f"Table name '{name}' is too long (max 100 characters)"}
    
    # Check for invalid characters
    # Google Sheets doesn't allow: [ ] * ? / \
    invalid_chars = ['[', ']', '*', '?', '/', '\\']
    for char in invalid_chars:
        if char in name:
            return {"valid": False, "error": f"Table name '{name}' contains invalid character '{char}'"}
    
    # Check for reserved names
    reserved_names = ['Table1', 'Table2', 'Table3']  # Common default names
    if name in reserved_names:
        return {"valid": False, "error": f"Table name '{name}' is a reserved name"}
    
    return {"valid": True, "cleaned_name": name}

def validate_column_name(name: str) -> Dict[str, Any]:
    """
    Validate a column name according to Google Sheets rules.
    
    Args:
        name: Column name to validate
    
    Returns:
        Dictionary with validation result
    """
    if not name or name.strip() == "":
        return {"valid": False, "error": "Column name cannot be empty"}
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Check length (Google Sheets limit is 100 characters)
    if len(name) > 100:
        return {"valid": False, "error": f"Column name '{name}' is too long (max 100 characters)"}
    
    # Check for invalid characters
    invalid_chars = ['[', ']', '*', '?', '/', '\\']
    for char in invalid_chars:
        if char in name:
            return {"valid": False, "error": f"Column name '{name}' contains invalid character '{char}'"}
    
    return {"valid": True, "cleaned_name": name}

def validate_column_type(col_type: str) -> Dict[str, Any]:
    """
    Validate a column type.
    
    Args:
        col_type: Column type to validate
    
    Returns:
        Dictionary with validation result
    """
    valid_types = [
        "COLUMN_TYPE_UNSPECIFIED",  # An unspecified column type
        "DOUBLE",                   # The number column type
        "CURRENCY",                 # The currency column type
        "PERCENT",                  # The percent column type
        "DATE",                     # The date column type
        "TIME",                     # The time column type
        "DATE_TIME",                # The date and time column type
        "TEXT",                     # The text column type
        "BOOLEAN",                  # The boolean column type
        "DROPDOWN",                 # The dropdown column type
        "NONE"                      # Legacy support - maps to TEXT
    ]
    if col_type not in valid_types:
        return {"valid": False, "error": f"Invalid column type '{col_type}'. Valid types: {', '.join(valid_types)}"}
    
    return {"valid": True, "cleaned_type": col_type}

def validate_cell_value(value: Union[str, int, float, bool, None]) -> Dict[str, Any]:
    """
    Validate a cell value.
    
    Args:
        value: Value to validate
    
    Returns:
        Dictionary with validation result
    """
    if value is None:
        return {"valid": True, "cleaned_value": None}
    
    # Check for string length limit
    if isinstance(value, str) and len(value) > 50000:
        return {"valid": False, "error": "String value is too long (max 50,000 characters)"}
    
    # Check for numeric limits
    if isinstance(value, (int, float)):
        if value > 1e15 or value < -1e15:
            return {"valid": False, "error": "Numeric value is too large (max 1e15)"}
    
    return {"valid": True, "cleaned_value": value}

def get_table_info(
    sheets_service,
    spreadsheet_id: str,
    table_id: str
) -> Dict[str, Any]:
    """
    Get comprehensive information about a specific table.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        table_id: ID of the table
    
    Returns:
        Dict containing comprehensive table information
    
    Raises:
        RuntimeError: If table is not found or API error occurs
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized")
    
    if not spreadsheet_id:
        raise RuntimeError("Spreadsheet ID is required")
    
    if not table_id:
        raise RuntimeError("Table ID is required")
    
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables,sheets.tables.columnProperties"
        ).execute()
        
        # Search for the table across all sheets
        for sheet in result.get("sheets", []):
            tables = sheet.get("tables", [])
            for table in tables:
                if table.get("tableId") == table_id:
                    table_range = table.get("range", {})
                    start_row = table_range.get("startRowIndex", 0)
                    end_row = table_range.get("endRowIndex", 0)
                    start_col = table_range.get("startColumnIndex", 0)
                    end_col = table_range.get("endColumnIndex", 0)
                    
                    # Calculate actual row and column counts from range
                    actual_row_count = end_row - start_row
                    actual_column_count = end_col - start_col
                    
                    # Get column properties if available
                    column_properties = table.get("columnProperties", [])
                    columns = []
                    
                    for i, col_prop in enumerate(column_properties):
                        column_name = col_prop.get("columnName", f"Column {i+1}")
                        column_type = col_prop.get("columnType", "TEXT")
                        
                        # Check for data validation rules to identify dropdown columns
                        data_validation = col_prop.get("dataValidationRule", {})
                        if data_validation:
                            validation_condition = data_validation.get("condition", {})
                            if validation_condition.get("type") == "ONE_OF_LIST":
                                column_type = "DROPDOWN"
                        
                        column_info = {
                            "name": column_name,
                            "type": column_type,
                            "index": i
                        }
                        # Preserve dataValidationRule if it exists
                        if data_validation:
                            column_info["dataValidationRule"] = data_validation
                        columns.append(column_info)
                    
                    # Calculate range notation
                    range_notation = f"{column_index_to_letter(start_col)}{start_row + 1}:{column_index_to_letter(end_col - 1)}{end_row}"
                    
                    return {
                        "table_id": table_id,
                        "table_name": table.get("displayName") or table.get("name") or f"Table{table_id}",
                        "range": table_range,
                        "column_count": actual_column_count,
                        "row_count": actual_row_count,
                        "start_row": start_row,
                        "end_row": end_row,
                        "start_col": start_col,
                        "end_col": end_col,
                        "range_notation": range_notation,
                        "columns": columns
                    }
        
        raise RuntimeError(f"Table with ID '{table_id}' not found")
        
    except HttpError as error:
        raise RuntimeError(f"Google Sheets API error getting table info: {error}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error getting table info: {str(error)}")

def get_table_ids_by_names(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str,
    table_names: List[str]
) -> Dict[str, Optional[str]]:
    """
    Get table IDs from spreadsheet ID, sheet name, and table names.
    
    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet
        table_names: List of table names to find
    
    Returns:
        Dictionary mapping table names to their IDs (None if not found)
    
    Raises:
        RuntimeError: If Google Sheets service not initialized
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set Google credentials environment variables.")
    
    if not spreadsheet_id:
        raise RuntimeError("Spreadsheet ID is required")
    
    if not sheet_name:
        raise RuntimeError("Sheet name is required")
    
    if not table_names:
        return {}
    
    try:
        # Get spreadsheet metadata to find tables
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        # Find the specific sheet
        target_sheet = None
        for sheet in result.get("sheets", []):
            props = sheet.get("properties", {})
            if props.get("title") == sheet_name:
                target_sheet = sheet
                break
        
        if not target_sheet:
            return {name: None for name in table_names}
        
        # Create lookup dictionary for all tables in the sheet
        table_lookup = {}
        tables = target_sheet.get("tables", [])
        
        for table in tables:
            table_id = table.get("tableId")
            # Try different possible name fields for table names
            table_name = table.get("displayName") or table.get("name") or f"Table{table_id}" if table_id else "Unknown"
            table_lookup[table_name] = table_id
        
        # Return results for requested table names
        results = {}
        for table_name in table_names:
            results[table_name] = table_lookup.get(table_name)
        
        return results
        
    except HttpError as error:
        print(f"Error getting table IDs for spreadsheet '{spreadsheet_id}': {error}")
        return {name: None for name in table_names}
    except Exception as error:
        print(f"Unexpected error while getting table IDs: {error}")
        return {name: None for name in table_names}

def check_duplicate_table_name(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str,
    table_name: str
) -> Dict[str, Any]:
    """
    Check if a table name already exists in the sheet.
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet
        table_name: Table name to check
    
    Returns:
        Dictionary with duplicate check results
    """
    try:
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.tables"
        ).execute()
        
        for sheet in result.get("sheets", []):
            if sheet.get("properties", {}).get("title") == sheet_name:
                tables = sheet.get("tables", [])
                for table in tables:
                    existing_name = table.get("displayName") or table.get("name") or f"Table{table.get('tableId', '')}"
                    if existing_name == table_name:
                        return {
                            "has_duplicate": True,
                            "error": f"Table with name '{table_name}' already exists in sheet '{sheet_name}'"
                        }
        
        return {"has_duplicate": False}
        
    except Exception as e:
        return {
            "has_duplicate": False,
            "warning": f"Could not verify against existing tables: {str(e)}"
        }

def column_index_to_letter(column_index: int) -> str:
    """
    Convert a column index to Excel-style column letter.
    
    Args:
        column_index: 0-based column index
    
    Returns:
        str: Column letter (A, B, C, ..., Z, AA, AB, ...)
        
    Examples:
        column_index_to_letter(0) -> "A"
        column_index_to_letter(25) -> "Z"
        column_index_to_letter(26) -> "AA"
        column_index_to_letter(27) -> "AB"
    """
    if column_index < 0:
        raise ValueError("Column index must be non-negative")
    
    # Convert to 1-based for Excel algorithm
    column_index_1based = column_index + 1
    
    result = ""
    while column_index_1based > 0:
        column_index_1based -= 1
        result = chr(65 + (column_index_1based % 26)) + result
        column_index_1based //= 26
    
    return result

def letter_to_column_index(column_letter: str) -> int:
    """
    Convert Excel-style column letter to column index.
    
    Args:
        column_letter: Column letter (A, B, C, ..., Z, AA, AB, ...)
    
    Returns:
        int: 0-based column index
        
    Examples:
        letter_to_column_index("A") -> 0
        letter_to_column_index("Z") -> 25
        letter_to_column_index("AA") -> 26
        letter_to_column_index("AB") -> 27
    """
    if not column_letter:
        raise ValueError("Column letter cannot be empty")
    
    column_letter = column_letter.upper()
    result = 0
    
    for char in column_letter:
        if not char.isalpha():
            raise ValueError(f"Invalid character in column letter: {char}")
        
        result = result * 26 + (ord(char) - ord('A') + 1)
    
    return result - 1  # Convert to 0-based index

def parse_cell_reference(cell: str) -> Tuple[int, int]:
    """
    Parse A1 notation cell reference to row and column indices.
    
    Args:
        cell: Cell reference in A1 notation (e.g., "A1", "B5")
    
    Returns:
        Tuple of (row_index, column_index) - both 0-based
    
    Raises:
        ValueError: If cell reference is invalid
    """
    # Extract column letters and row number
    match = re.match(r'^([A-Z]+)(\d+)$', cell.upper())
    if not match:
        raise ValueError(f"Invalid cell reference: {cell}")
    
    column_letters = match.group(1)
    row_number = int(match.group(2))
    
    # Convert column letters to index
    column_index = letter_to_column_index(column_letters)
    
    # Convert row number to index (1-based to 0-based)
    row_index = row_number - 1
    
    return row_index, column_index

def map_column_type(col_type: str) -> str:
    """
    Map user-friendly column types to Google Sheets API types.
    
    Args:
        col_type: User-friendly column type
    
    Returns:
        str: Google Sheets API column type
    """
    api_type_mapping = {
        "COLUMN_TYPE_UNSPECIFIED": "COLUMN_TYPE_UNSPECIFIED",
        "DOUBLE": "DOUBLE",
        "CURRENCY": "CURRENCY",
        "PERCENT": "PERCENT",
        "DATE": "DATE",
        "TIME": "TIME",
        "DATE_TIME": "DATE_TIME",
        "TEXT": "TEXT",
        "BOOLEAN": "BOOLEAN",
        "DROPDOWN": "DROPDOWN",
        "NONE": "TEXT",  # Legacy support
        # Legacy mappings for backward compatibility
        "NUMBER": "DOUBLE",
        "CHECKBOX": "BOOLEAN"
    }
    
    # Handle case-insensitive input
    col_type_upper = col_type.upper() if col_type else "TEXT"
    return api_type_mapping.get(col_type_upper, "TEXT")

def create_cell_with_formatting(
    value: Union[str, int, float, bool, None],
    column_type: str
) -> dict:
    """
    Create a cell with proper formatting based on column type.
    
    Args:
        value: Cell value
        column_type: Column type for formatting
    
    Returns:
        dict: Cell data with formatting
    """
    if value is None:
        return {"userEnteredValue": {"stringValue": ""}}
    
    # Create cell value based on type
    if isinstance(value, bool):
        cell_value = {"userEnteredValue": {"boolValue": value}}
    elif isinstance(value, int):
        cell_value = {"userEnteredValue": {"numberValue": float(value)}}
    elif isinstance(value, float):
        cell_value = {"userEnteredValue": {"numberValue": value}}
    else:
        # Convert to string for all other types
        cell_value = {"userEnteredValue": {"stringValue": str(value)}}
    
    # Add formatting based on column type
    if column_type in ["DOUBLE", "PERCENT", "CURRENCY"]:
        cell_value["userEnteredFormat"] = {
            "numberFormat": get_number_format_for_type(column_type)
        }
    elif column_type in ["DATE", "TIME", "DATE_TIME"]:
        cell_value["userEnteredFormat"] = {
            "numberFormat": get_number_format_for_type(column_type)
        }
    
    return cell_value

def get_number_format_for_type(col_type: str) -> dict:
    """
    Get number format for different column types.
    
    Args:
        col_type: Column type
    
    Returns:
        dict: Number format specification
    """
    if col_type == "PERCENT":
        return {"type": "PERCENT", "pattern": "0.00%"}
    elif col_type == "CURRENCY":
        return {"type": "CURRENCY", "pattern": "$#,##0.00"}
    elif col_type == "DOUBLE":
        return {"type": "NUMBER", "pattern": "#,##0.00"}
    elif col_type == "TIME":
        return {"type": "TIME", "pattern": "hh:mm:ss"}
    elif col_type == "DATE_TIME":
        return {"type": "DATE_TIME", "pattern": "yyyy-mm-dd hh:mm:ss"}
    elif col_type == "DATE":
        return {"type": "DATE", "pattern": "yyyy-mm-dd"}
    elif col_type == "BOOLEAN":
        return {"type": "TEXT"}  # Boolean doesn't need number formatting
    elif col_type == "DROPDOWN":
        return {"type": "TEXT"}  # Dropdown doesn't need number formatting
    elif col_type == "COLUMN_TYPE_UNSPECIFIED":
        return {"type": "TEXT"}  # Unspecified defaults to text
    else:
        return {"type": "TEXT"}

def validate_row_data(
    row: List[Union[str, int, float, bool, None]],
    column_count: int
) -> Dict[str, Any]:
    """
    Validate a row of data.
    
    Args:
        row: Row data to validate
        column_count: Expected number of columns
    
    Returns:
        Dictionary with validation result
    """
    if not isinstance(row, list):
        return {"valid": False, "error": "Row must be a list of values"}
    
    if len(row) != column_count:
        return {"valid": False, "error": f"Row has {len(row)} values but table has {column_count} columns"}
    
    # Validate individual cell values
    validated_cells = []
    invalid_cells = []
    
    for i, cell_value in enumerate(row):
        cell_validation = validate_cell_value(cell_value)
        if cell_validation["valid"]:
            validated_cells.append(cell_validation["cleaned_value"])
        else:
            invalid_cells.append({"index": i, "value": cell_value, "error": cell_validation["error"]})
    
    if invalid_cells:
        return {"valid": False, "error": f"Invalid cell values: {invalid_cells}"}
    
    return {"valid": True, "cleaned_row": validated_cells} 