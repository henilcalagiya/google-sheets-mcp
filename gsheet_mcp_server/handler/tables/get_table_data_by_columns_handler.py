"""Handler for getting table data by columns in Google Sheets."""

from typing import Dict, List, Union, Optional
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    column_index_to_letter,
    letter_to_column_index
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def get_table_data_by_columns_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    column_names: List[str],
    start_row: Optional[int] = None,
    end_row: Optional[int] = None,
    include_headers: bool = True
) -> str:
    """
    Get table data by specific columns using the spreadsheets.values.get API.
    
    This handler retrieves data for specific columns using column names.
    Uses the spreadsheets.values.get API for efficient column-based data retrieval.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to read data from
        column_names: List of column names to retrieve
        start_row: Starting row index (0-based, optional)
        end_row: Ending row index (0-based, optional)
        include_headers: Whether to include header row in results
    
    Returns:
        str: Success message with column data or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        # Validate column names
        if not column_names or not isinstance(column_names, list) or len(column_names) == 0:
            return compact_json_response({
                "success": False,
                "message": "column_names must be a non-empty list."
            })
        
        # Validate row indices
        if start_row is not None and start_row < 0:
            return compact_json_response({
                "success": False,
                "message": "start_row must be non-negative."
            })
        
        if end_row is not None and end_row < 0:
            return compact_json_response({
                "success": False,
                "message": "end_row must be non-negative."
            })
        
        if start_row is not None and end_row is not None and start_row >= end_row:
            return compact_json_response({
                "success": False,
                "message": "start_row must be less than end_row."
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
        
        # Get table information to understand structure
        try:
            table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
            table_range = table_info.get('range', {})
            columns = table_info.get('columns', [])
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve table information: {str(e)}"
            })
        
        # Extract table range information
        start_row_index = table_range.get('startRowIndex', 0)
        end_row_index = table_range.get('endRowIndex', 0)
        start_column_index = table_range.get('startColumnIndex', 0)
        end_column_index = table_range.get('endColumnIndex', 0)
        
        # Convert column names to indices
        column_name_to_index = {col.get('name', ''): col.get('index', 0) for col in columns}
        target_column_indices = []
        
        for col_name in column_names:
            if col_name not in column_name_to_index:
                return compact_json_response({
                    "success": False,
                    "message": f"Column '{col_name}' not found in table."
                })
            target_column_indices.append(column_name_to_index[col_name])
        
        # Sort column indices to maintain order
        target_column_indices.sort()
        
        # Convert column indices to letters for API call
        column_letters = []
        for col_index in target_column_indices:
            # Convert to absolute column index (add table's start column)
            absolute_col_index = start_column_index + col_index
            column_letter = column_index_to_letter(absolute_col_index)
            column_letters.append(column_letter)
        
        # Create range string for API call
        if len(column_letters) == 1:
            range_string = f"{sheet_name}!{column_letters[0]}:{column_letters[0]}"
        else:
            range_string = f"{sheet_name}!{column_letters[0]}:{column_letters[-1]}"
        
        # Adjust range for row limits if specified
        if start_row is not None or end_row is not None:
            actual_start_row = start_row if start_row is not None else start_row_index
            actual_end_row = end_row if end_row is not None else end_row_index
            
            # Convert to 1-based row numbers for API
            start_row_num = actual_start_row + 1
            end_row_num = actual_end_row
            
            range_string = f"{sheet_name}!{column_letters[0]}{start_row_num}:{column_letters[-1]}{end_row_num}"
        
        # Get column data using spreadsheets.values.get
        try:
            values_response = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_string
            ).execute()
            
            values = values_response.get('values', [])
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve column data: {str(e)}"
            })
        
        # Process the data
        column_data = {}
        processed_rows = []
        
        # Get column names for the target columns
        target_column_names = []
        for col_index in target_column_indices:
            if col_index < len(columns):
                col_name = columns[col_index].get('name', f'Column {col_index}')
                target_column_names.append(col_name)
            else:
                target_column_names.append(f'Column {col_index}')
        
        # Process each row
        for row_index, row in enumerate(values):
            # Skip header row if not included
            if not include_headers and row_index == 0:
                continue
            
            # Create row data with column mapping
            row_data = {}
            for i, col_name in enumerate(target_column_names):
                if i < len(row):
                    row_data[col_name] = row[i]
                else:
                    row_data[col_name] = None
            
            processed_rows.append({
                "row_index": row_index,
                "data": row_data
            })
        
        # Prepare response data
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_name": table_name,
            "columns_requested": target_column_names,
            "column_indices": target_column_indices,
            "range_used": range_string,
            "total_rows": len(processed_rows),
            "rows": processed_rows,
            "message": f"Successfully retrieved data for {len(target_column_names)} column(s) from table '{table_name}'"
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
            "message": f"Error getting table data by columns: {str(e)}"
        }) 