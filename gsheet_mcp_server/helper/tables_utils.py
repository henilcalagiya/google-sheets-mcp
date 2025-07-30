"""Helper utilities for Google Sheets table operations."""

from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError


def get_table_info(
    sheets_service,
    spreadsheet_id: str,
    table_id: str
) -> Dict[str, Any]:
    """
    Get comprehensive information about a specific table.
    
    This function retrieves detailed metadata about a table including:
    - Table properties (name, range, column/row counts)
    - Range boundaries (start/end row/column indices)
    - Calculated dimensions from range
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        table_id: ID of the table
    
    Returns:
        Dict containing comprehensive table information with keys:
        - table_id: The table's unique identifier
        - table_name: Human-readable name of the table
        - range: Dictionary with start/end row/column indices
        - column_count: Number of columns in the table
        - row_count: Number of rows in the table
        - start_row, end_row, start_col, end_col: Position boundaries
        
    Raises:
        RuntimeError: If table is not found or API error occurs
    """
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
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
                    
                    return {
                        "table_id": table_id,
                        "table_name": table.get("name", "Unknown"),
                        "range": table_range,
                        "column_count": actual_column_count,
                        "row_count": actual_row_count,
                        "start_row": start_row,
                        "end_row": end_row,
                        "start_col": start_col,
                        "end_col": end_col
                    }
        
        raise RuntimeError(f"Table with ID '{table_id}' not found")
        
    except HttpError as error:
        raise RuntimeError(f"Google Sheets API error getting table info: {error}")
    except Exception as error:
        raise RuntimeError(f"Error getting table info: {error}")


def get_table_info_simple(
    sheets_service,
    spreadsheet_id: str,
    table_id: str
) -> Dict[str, Any]:
    """
    Get basic information about a specific table (simpler version).
    
    This function retrieves basic metadata about a table using the
    columnProperties and rowsProperties arrays from the API response.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        table_id: ID of the table
    
    Returns:
        Dict containing basic table information with keys:
        - table_id: The table's unique identifier
        - table_name: Human-readable name of the table
        - range: Dictionary with start/end row/column indices
        - column_count: Number of columns from columnProperties
        - row_count: Number of rows from rowsProperties
        
    Raises:
        RuntimeError: If table is not found or API error occurs
    """
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        # Search for the table across all sheets
        for sheet in result.get("sheets", []):
            tables = sheet.get("tables", [])
            for table in tables:
                if table.get("tableId") == table_id:
                    return {
                        "table_id": table_id,
                        "table_name": table.get("name", "Unknown"),
                        "range": table.get("range", {}),
                        "column_count": len(table.get("columnProperties", [])),
                        "row_count": len(table.get("rowsProperties", [])) if table.get("rowsProperties") else 0
                    }
        
        raise RuntimeError(f"Table with ID '{table_id}' not found")
        
    except HttpError as error:
        raise RuntimeError(f"Google Sheets API error getting table info: {error}")
    except Exception as error:
        raise RuntimeError(f"Error getting table info: {error}")


def get_table_ids_by_names(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str,
    table_names: List[str]
) -> Dict[str, Optional[str]]:
    """
    Get table IDs from spreadsheet ID, sheet name, and table names.
    Works for both single and multiple table lookups.
    
    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet containing the tables
        table_names: List of table names to find (can be single item)
    
    Returns:
        Dictionary mapping table names to their IDs (None if not found)
        
    Examples:
        # Single table lookup
        result = get_table_ids_by_names(sheets_service, "123", "Sheet1", ["SalesData"])
        # Returns: {"SalesData": "4567890123"}
        
        # Multiple table lookup
        result = get_table_ids_by_names(sheets_service, "123", "Sheet1", ["SalesData", "Inventory", "Summary"])
        # Returns: {"SalesData": "4567890123", "Inventory": "7890123456", "Summary": None}
    
    Raises:
        RuntimeError: If Google Sheets service not initialized
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        # Find the specific sheet
        for sheet in result.get("sheets", []):
            props = sheet.get("properties", {})
            if props.get("title") == sheet_name:
                tables = sheet.get("tables", [])
                
                # Create lookup dictionary for all tables in this sheet
                table_lookup = {}
                for table in tables:
                    table_name = table.get("name")
                    table_id = table.get("tableId")
                    if table_name and table_id:  # Only add if both name and ID exist
                        table_lookup[table_name] = table_id
                
                # Return results for requested table names
                results = {}
                for table_name in table_names:
                    results[table_name] = table_lookup.get(table_name)
                
                return results
        
        # Sheet not found, return None for all requested table names
        return {name: None for name in table_names}
        
    except HttpError as error:
        print(f"Error getting table IDs for spreadsheet '{spreadsheet_id}' sheet '{sheet_name}': {error}")
        return {name: None for name in table_names}
    except Exception as error:
        print(f"Unexpected error while getting table IDs: {error}")
        return {name: None for name in table_names} 