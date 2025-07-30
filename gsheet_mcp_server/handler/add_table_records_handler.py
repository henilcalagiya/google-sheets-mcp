"""
Handler for appending cells to native Google Sheets tables using AppendCellsRequest.

This module provides functionality to add new cells/data to existing table objects.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from ..helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names


class AddTableRecordsRequest(BaseModel):
    """Request model for appending/inserting records to native Google Sheets tables."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet containing the table")
    table_name: str = Field(..., description="Name of the table to append/insert records to")
    data: List[List[str]] = Field(..., description="2D list of data rows to append/insert")
    operation: str = Field(default="APPEND", description="Operation type: APPEND or INSERT")
    position: int = Field(default=None, description="Position to insert data (0-based, required for INSERT operation)")
    append_position: str = Field(default="END", description="Where to append: START or END (for APPEND operation)")


def add_table_records(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    data: List[List[str]],
    operation: str = "APPEND",
    position: int = None,
    append_position: str = "END"
) -> Dict[str, Any]:
    """
    Add records to a native Google Sheets table using a simplified, unified approach.
    
    This tool uses a single, reliable pattern:
    1. Get table information and current data
    2. Calculate new data positions
    3. Insert rows if needed (for INSERT operations)
    4. Write data to calculated positions
    5. Let Google Sheets handle table range updates automatically
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add records to
        data: 2D list of data rows to add
        operation: Operation type ("APPEND" or "INSERT")
        position: Position to insert data (0-based, required for INSERT)
        append_position: Where to append (START or END, for APPEND operation)
    
    Returns:
        Dict containing operation results with table information
        
    Raises:
        RuntimeError: If table operation fails
    """
    try:
        # Validate operation and parameters
        if operation not in ["APPEND", "INSERT"]:
            raise RuntimeError("Operation must be 'APPEND' or 'INSERT'")
        
        if operation == "INSERT" and position is None:
            raise RuntimeError("Position is required for INSERT operation")
        
        if operation == "INSERT" and position < 0:
            raise RuntimeError("Position must be >= 0 for INSERT operation")
        
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            raise RuntimeError(f"Spreadsheet '{spreadsheet_name}' not found")
        
        # Get sheet ID
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            raise RuntimeError(f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'")
        
        # Get table ID from table name
        table_id = get_table_id_by_name(sheets_service, spreadsheet_id, sheet_name, table_name)
        if table_id is None:
            raise RuntimeError(f"Table '{table_name}' not found in sheet '{sheet_name}'")
        
        # Get current table information
        table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        table_range = table_info.get("range", {})
        current_row_count = table_info.get("row_count", 0)
        
        # Calculate target positions based on operation
        if operation == "APPEND":
            if append_position == "END":
                # Append to end: insert after the last data row
                target_start_row = table_range.get("endRowIndex", 0)
            else:  # START
                # Append to start: insert after header row
                target_start_row = table_range.get("startRowIndex", 0) + 1
        else:  # INSERT
            # Insert at specific position: calculate actual sheet position
            target_start_row = table_range.get("startRowIndex", 0) + 1 + position
        
        # Convert data to simple values
        values = []
        for row in data:
            row_values = []
            for cell_value in row:
                # Convert to appropriate type
                if isinstance(cell_value, (int, float)):
                    row_values.append(cell_value)
                elif isinstance(cell_value, bool):
                    row_values.append(cell_value)
                else:
                    row_values.append(str(cell_value))
            values.append(row_values)
        
        # Step 1: Handle operations differently for better efficiency
        if operation == "APPEND":
            # For APPEND: Use values().append which is more efficient and handles table expansion
            range_name = f"{sheet_name}!A{target_start_row + 1}"
            
            # Use values().append for APPEND operations
            response = sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": values}
            ).execute()
            
            # No need for manual table range update - values().append handles it automatically
            
        else:  # INSERT operation
            # For INSERT: Use values().update (simpler than batchUpdate with updateCells)
            range_name = f"{sheet_name}!A{target_start_row + 1}"
            
            # Insert empty rows first using insertDimension
            insert_request = {
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "ROWS",
                                "startIndex": target_start_row,
                                "endIndex": target_start_row + len(values)
                            },
                            "inheritFromBefore": True
                        }
                    }
                ]
            }
            
            # Execute the insert dimension request
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=insert_request
            ).execute()
            
            # Then write data using values().update (simpler than updateCells)
            response = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body={"values": values}
            ).execute()
        
        # Get updated table info to confirm changes
        updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
        new_row_count = updated_table_info.get("row_count", current_row_count + len(values))
        
        # Prepare response message
        operation_text = "appended" if operation == "APPEND" else "inserted"
        position_text = f" at position {position}" if operation == "INSERT" else f" to {append_position.lower()}"
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "table_id": table_id,
            "operation": operation,
            "position": position if operation == "INSERT" else None,
            "append_position": append_position if operation == "APPEND" else None,
            "rows_affected": len(values),
            "new_row_count": new_row_count,
            "target_range": f"{sheet_name}!A{target_start_row + 1}:Z{target_start_row + len(values)}",
            "message": f"Successfully {operation_text} {len(values)} rows{position_text} in table '{table_name}'"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details and len(error.error_details) > 0 else {}
        error_message = error_details.get('message', str(error)) if isinstance(error_details, dict) else str(error)
        raise RuntimeError(f"Error operating on table cells: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error operating on table cells: {error}")


def get_table_id_by_name(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str,
    table_name: str
) -> str:
    """
    Get table ID from table name.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet
        table_name: Name of the table
    
    Returns:
        Table ID if found, None otherwise
    """
    try:
        # Get spreadsheet to find table information
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        # Search for the table in the specified sheet
        for sheet in result.get("sheets", []):
            if sheet.get("properties", {}).get("title") == sheet_name:
                tables = sheet.get("tables", [])
                for table in tables:
                    if table.get("name") == table_name:
                        return table.get("tableId")
                break
        
        return None
        
    except Exception as error:
        raise RuntimeError(f"Error getting table ID: {error}")


def get_table_info(
    sheets_service,
    spreadsheet_id: str,
    table_id: str
) -> Dict[str, Any]:
    """
    Get information about a specific table.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        table_id: ID of the table
    
    Returns:
        Dict containing table information
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
        
    except Exception as error:
        raise RuntimeError(f"Error getting table info: {error}")