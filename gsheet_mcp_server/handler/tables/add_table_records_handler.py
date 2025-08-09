"""Handler for adding records (rows) into tables in Google Sheets."""

from typing import List, Dict, Any, Union, Optional
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    get_table_ids_by_names,
    get_table_info,
    validate_row_data,
    create_cell_with_formatting
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def add_table_records_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str,
    records: List[List[Union[str, int, float, bool, None]]]
) -> str:
    """
    Add records (rows) into a table in Google Sheets using InsertRangeRequest, UpdateCellsRequest, and UpdateTableRequest.
    
    According to the official Google Sheets API documentation, to add records into a table:
    1. Use InsertRangeRequest to insert new rows at the end of the table
    2. Use UpdateCellsRequest to write values into the inserted rows
    3. Use UpdateTableRequest to update the table's range to include the new rows
    4. Each record must match the table's column structure
    5. Values are automatically formatted based on column types
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add records into
        records: List of records, where each record is a list of values matching table columns
    
    Returns:
        str: Success message with operation details or error message
    """
    try:
        # Validate inputs
        if not table_name or table_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Table name is required."
            })
        
        if not records or not isinstance(records, list):
            return compact_json_response({
                "success": False,
                "message": "Records are required and must be a list of record lists."
            })
        
        if len(records) == 0:
            return compact_json_response({
                "success": False,
                "message": "At least one record must be provided."
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
        
        # Get table information
        try:
            table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
            table_range = table_info.get('range', {})
            current_column_count = table_info.get('column_count', 0)
            columns = table_info.get('columns', [])
        except Exception as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve information for table '{table_name}': {str(e)}"
            })
        
        if current_column_count == 0:
            return compact_json_response({
                "success": False,
                "message": f"Table '{table_name}' has no columns defined."
            })
        
        # Get table boundaries
        table_start_row = table_range.get("startRowIndex", 0)
        table_end_row = table_range.get("endRowIndex", 0)
        table_start_col = table_range.get("startColumnIndex", 0)
        table_end_col = table_range.get("endColumnIndex", 0)
        
        # Always insert at the end of the table
        insert_row_index = table_end_row
        
        # Validate and process each record
        validated_records = []
        for i, record in enumerate(records):
            if not isinstance(record, list):
                return compact_json_response({
                    "success": False,
                    "message": f"Record {i + 1} must be a list of values."
                })
            
            # Validate record data structure against table columns
            record_validation = validate_row_data(record, current_column_count)
            if not record_validation["valid"]:
                return compact_json_response({
                    "success": False,
                    "message": f"Invalid record {i + 1}: {record_validation['error']}"
                })
            
            validated_records.append(record_validation["cleaned_row"])
        
        # Create batch update requests
        requests = []
        
        # 1. InsertRangeRequest to insert rows
        insert_range_request = {
            "insertRange": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": insert_row_index,
                    "endRowIndex": insert_row_index + len(validated_records),
                    "startColumnIndex": table_start_col,
                    "endColumnIndex": table_end_col
                },
                "shiftDimension": "ROWS"
            }
        }
        requests.append(insert_range_request)
        
        # 2. UpdateCellsRequest to set values in the inserted rows
        rows_data = []
        for record in validated_records:
            row_values = []
            for i, cell_value in enumerate(record):
                # Get column type for proper formatting
                column_type = "TEXT"  # Default type
                if i < len(columns):
                    column_type = columns[i].get("type", "TEXT")
                
                # Create cell data with proper formatting
                cell_data = create_cell_with_formatting(cell_value, column_type)
                row_values.append(cell_data)
            
            rows_data.append({"values": row_values})
        
        update_cells_request = {
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": insert_row_index,
                    "endRowIndex": insert_row_index + len(validated_records),
                    "startColumnIndex": table_start_col,
                    "endColumnIndex": table_end_col
                },
                "rows": rows_data,
                "fields": "*"
            }
        }
        requests.append(update_cells_request)
        
        # 3. UpdateTableRequest to update the table's range after inserting rows
        # Calculate new end row index: original end + number of inserted rows
        new_end_row_index = table_end_row + len(validated_records)
        
        update_table_request = {
            "updateTable": {
                "table": {
                    "tableId": table_id,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": table_start_row,
                        "endRowIndex": new_end_row_index,  # Extend table range to include new rows
                        "startColumnIndex": table_start_col,
                        "endColumnIndex": table_end_col
                    }
                },
                "fields": "range"
            }
        }
        requests.append(update_table_request)
        
        # Execute the batch update request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        
        # Extract response information
        replies = response.get("replies", [])
        if replies and len(replies) >= 3:
            insert_result = replies[0].get("insertRange", {})
            update_result = replies[1].get("updatedCells", {})
            update_table_result = replies[2].get("updateTable", {})
            
            # Get updated table information
            try:
                updated_table_info = get_table_info(sheets_service, spreadsheet_id, table_id)
                updated_range = updated_table_info.get('range', {})
                updated_row_count = updated_table_info.get('row_count', 0)
            except Exception:
                updated_range = {}
                updated_row_count = 0
            
            response_data = {
                "success": True,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "table_name": table_name,
                "records_inserted": len(validated_records),
                "insert_row_index": insert_row_index,
                "updated_range": updated_range,
                "updated_row_count": updated_row_count,
                "inserted_records": validated_records,
                "message": f"Successfully inserted {len(validated_records)} record(s) into table '{table_name}' in '{sheet_name}' at the end"
            }
            
            return compact_json_response(response_data)
        else:
            return compact_json_response({
                "success": False,
                "message": "Failed to insert records - insufficient response data from API (expected 3 operations)"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error inserting table records: {str(e)}"
        }) 