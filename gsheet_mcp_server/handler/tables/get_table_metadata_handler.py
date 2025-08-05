"""Handler for getting table metadata from Google Sheets."""

from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.sheets_utils import get_sheet_ids_by_names
from gsheet_mcp_server.helper.tables_utils import (
    validate_table_name,
    get_table_ids_by_names,
    get_table_info,
    column_index_to_letter
)
from gsheet_mcp_server.helper.json_utils import compact_json_response

def get_table_metadata_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    table_name: str = None
) -> str:
    """
    Get comprehensive metadata for a specific table in Google Sheets.
    If table_name is not provided, returns a list of all tables in the sheet.
    
    Args:
        drive_service: Google Drive service instance
        sheets_service: Google Sheets service instance
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to get metadata for (optional)
    
    Returns:
        str: JSON-formatted string containing table metadata or list of all tables
    """
    try:
        # Validate inputs
        if not spreadsheet_name or spreadsheet_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Spreadsheet name is required."
            })
        
        if not sheet_name or sheet_name.strip() == "":
            return compact_json_response({
                "success": False,
                "message": "Sheet name is required."
            })
        
        # Validate table name if provided
        if table_name:
            table_validation = validate_table_name(table_name)
            if not table_validation["valid"]:
                return compact_json_response({
                    "success": False,
                    "message": table_validation["error"]
                })
            validated_table_name = table_validation["cleaned_name"]
        else:
            validated_table_name = None
        
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
        
        # If table_name is not provided, get all tables in the sheet
        if not validated_table_name:
            return _get_all_tables_metadata(sheets_service, spreadsheet_id, sheet_id, sheet_name, spreadsheet_name)
        
        # Get specific table metadata
        table_ids = get_table_ids_by_names(sheets_service, spreadsheet_id, sheet_name, [validated_table_name])
        table_id = table_ids.get(validated_table_name)
        if not table_id:
            return compact_json_response({
                "success": False,
                "message": f"Table '{validated_table_name}' not found in sheet '{sheet_name}'."
            })
        
        # Get comprehensive table metadata using the existing utility function
        try:
            table_metadata = get_table_info(sheets_service, spreadsheet_id, table_id)
            
            # Format the response for better readability
            formatted_metadata = {
                "table_name": table_metadata.get("table_name"),
                "table_id": table_metadata.get("table_id"),
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "dimensions": {
                    "column_count": table_metadata.get("column_count"),
                    "row_count": table_metadata.get("row_count")
                },
                "range": {
                    "start_row": table_metadata.get("start_row"),
                    "end_row": table_metadata.get("end_row"),
                    "start_column": table_metadata.get("start_col"),
                    "end_column": table_metadata.get("end_col")
                },
                "range_notation": f"A{table_metadata.get('start_row', 0) + 1}:{_get_column_letter(table_metadata.get('end_col', 0) - 1)}{table_metadata.get('end_row', 0)}",
                "columns": table_metadata.get("columns", [])
            }
            
            response_data = {
                "success": True,
                "message": f"Successfully retrieved metadata for table '{validated_table_name}'",
                "data": formatted_metadata
            }
            
            return compact_json_response(response_data)
            
        except RuntimeError as e:
            return compact_json_response({
                "success": False,
                "message": f"Could not retrieve metadata for table '{validated_table_name}': {str(e)}"
            })
        
    except HttpError as error:
        return compact_json_response({
            "success": False,
            "message": f"Google Sheets API error: {str(error)}"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error getting table metadata: {str(e)}"
        })

def _get_all_tables_metadata(
    sheets_service,
    spreadsheet_id: str,
    sheet_id: int,
    sheet_name: str,
    spreadsheet_name: str
) -> str:
    """
    Get metadata for all tables in a sheet.
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet
        sheet_name: Name of the sheet
        spreadsheet_name: Name of the spreadsheet
    
    Returns:
        str: JSON-formatted string containing all tables metadata
    """
    try:
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.tables"
        ).execute()
        
        all_tables = []
        total_tables = 0
        
        for sheet in result.get("sheets", []):
            if sheet.get("properties", {}).get("sheetId") == sheet_id:
                tables = sheet.get("tables", [])
                total_tables = len(tables)
                
                for table in tables:
                    table_id = table.get("tableId")
                    table_name = table.get("displayName") or table.get("name") or f"Table{table_id}"
                    
                    # Get basic table info
                    table_range = table.get("range", {})
                    start_row = table_range.get("startRowIndex", 0)
                    end_row = table_range.get("endRowIndex", 0)
                    start_col = table_range.get("startColumnIndex", 0)
                    end_col = table_range.get("endColumnIndex", 0)
                    
                    # Calculate dimensions
                    column_count = end_col - start_col
                    row_count = end_row - start_row
                    
                    # Get column information
                    columns = []
                    column_properties = table.get("columnProperties", [])
                    
                    for i, col_prop in enumerate(column_properties):
                        column_name = col_prop.get("columnName", f"Column {i+1}")
                        column_type = col_prop.get("columnType", "TEXT")
                        
                        # Check for data validation rules
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
                        
                        # Add dropdown options if available
                        if column_type == "DROPDOWN" and data_validation:
                            condition = data_validation.get("condition", {})
                            values = condition.get("values", [])
                            dropdown_options = [v.get("userEnteredValue", "") for v in values]
                            column_info["dropdown_options"] = dropdown_options
                        
                        columns.append(column_info)
                    
                    table_info = {
                        "table_id": table_id,
                        "table_name": table_name,
                        "dimensions": {
                            "column_count": column_count,
                            "row_count": row_count
                        },
                        "range": {
                            "start_row": start_row,
                            "end_row": end_row,
                            "start_column": start_col,
                            "end_column": end_col
                        },
                        "range_notation": f"A{start_row + 1}:{_get_column_letter(end_col - 1)}{end_row}",
                        "columns": columns
                    }
                    
                    all_tables.append(table_info)
                
                break
        
        response_data = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "total_tables": total_tables,
            "tables": all_tables,
            "message": f"Successfully retrieved metadata for {total_tables} table(s) in sheet '{sheet_name}'"
        }
        
        return compact_json_response(response_data)
        
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error getting all tables metadata: {str(e)}"
        })

def _get_column_letter(column_index: int) -> str:
    """Convert column index to letter notation."""
    try:
        return column_index_to_letter(column_index)
    except:
        return f"Column{column_index}" 