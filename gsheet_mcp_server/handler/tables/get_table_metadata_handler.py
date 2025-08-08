"""Handler for getting table metadata from Google Sheets."""

from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError
from datetime import datetime

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
    table_name: str = None,
    include_sample_data: bool = False,
    include_formulas: bool = False,
    include_formatting: bool = False,
    include_statistics: bool = False,
    max_sample_rows: int = 5,
    specific_columns: List[str] = None,
    exclude_metadata_types: List[str] = None
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
        include_sample_data: Whether to include sample data rows
        include_formulas: Whether to include formula information
        include_formatting: Whether to include cell formatting details
        include_statistics: Whether to include data statistics
        max_sample_rows: Maximum number of sample rows to return
        specific_columns: List of column names to get metadata for (optional)
        exclude_metadata_types: List of metadata types to exclude (optional)
    
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
        
        # Get spreadsheet ID and metadata
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })

        # Get spreadsheet metadata for modification info
        spreadsheet_metadata = drive_service.files().get(
            fileId=spreadsheet_id,
            fields="modifiedTime,lastModifyingUser"
        ).execute()

        # Get sheet ID and metadata
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
        sheet_id = sheet_ids.get(sheet_name)
        if sheet_id is None:
            return compact_json_response({
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
            })
        
        # Get sheet metadata
        sheet_metadata = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=[f"{sheet_name}"],
            includeGridData=include_formatting,
            fields="sheets(properties,merges,protectedRanges,basicFilter,conditionalFormats)"
        ).execute()
        
        sheet_props = sheet_metadata.get("sheets", [])[0].get("properties", {})
        
        # If table_name is not provided, get all tables in the sheet
        if not validated_table_name:
            return _get_all_tables_metadata(
                sheets_service, 
                spreadsheet_id, 
                sheet_id, 
                sheet_name, 
                spreadsheet_name,
                sheet_props,
                spreadsheet_metadata,
                include_sample_data,
                include_formulas,
                include_formatting,
                include_statistics,
                max_sample_rows,
                specific_columns,
                exclude_metadata_types
            )
        
        # Get specific table metadata
        # Get table ID and check for both displayName and name fields
        table_id = None
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.tables"
        ).execute()
        
        for sheet in result.get("sheets", []):
            tables = sheet.get("tables", [])
            for table in tables:
                table_display_name = table.get("displayName")
                table_name = table.get("name")
                if validated_table_name in [table_display_name, table_name]:
                    table_id = table.get("tableId")
                    break
            if table_id:
                break
        if not table_id:
            return compact_json_response({
                "success": False,
                "message": f"Table '{validated_table_name}' not found in sheet '{sheet_name}'."
            })
        
        try:
            # Get comprehensive table metadata
            table_metadata = get_table_info(sheets_service, spreadsheet_id, table_id)
            
            # Get table range for additional data
            start_col = table_metadata.get('start_col', 0)
            end_col = table_metadata.get('end_col', 0)
            start_row = table_metadata.get('start_row', 0)
            end_row = table_metadata.get('end_row', 0)
            table_range = f"{sheet_name}!{column_index_to_letter(start_col)}{start_row + 1}:{column_index_to_letter(end_col - 1)}{end_row}"
            
            # Get sample data if requested
            sample_data = None
            if include_sample_data:
                data_response = sheets_service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=table_range,
                    valueRenderOption="UNFORMATTED_VALUE" if not include_formulas else "FORMULA"
                ).execute()
                sample_data = data_response.get("values", [])[:max_sample_rows]
            
            # Get formatting if requested
            formatting_data = None
            if include_formatting:
                format_response = sheets_service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id,
                    ranges=[table_range],
                    fields="sheets(data(rowData(values(userEnteredFormat))))"
                ).execute()
                formatting_data = format_response.get("sheets", [])[0].get("data", [])[0].get("rowData", [])
            
            # Calculate statistics if requested
            statistics = None
            if include_statistics and sample_data:
                statistics = _calculate_statistics(sample_data)
            
            # Filter columns if specific ones requested
            columns = table_metadata.get("columns", [])
            if specific_columns:
                columns = [col for col in columns if col.get("name") in specific_columns]
            
            # Get frozen dimensions
            grid_properties = sheet_props.get("gridProperties", {})
            frozen_rows = grid_properties.get("frozenRowCount", 0)
            frozen_columns = grid_properties.get("frozenColumnCount", 0)
            
            # Get column dimensions
            column_metadata = sheet_props.get("columnMetadata", [])
            column_dimensions = []
            for i, col in enumerate(columns):
                col_index = table_metadata.get("start_col", 0) + i
                if col_index < len(column_metadata):
                    width = column_metadata[col_index].get("pixelSize")
                    column_dimensions.append({"index": i, "width": width})
            
            # Get merged ranges
            merges = sheet_metadata.get("sheets", [])[0].get("merges", [])
            table_merges = _filter_merges_for_table(merges, table_metadata)
            
            # Get conditional formatting
            conditional_formats = sheet_metadata.get("sheets", [])[0].get("conditionalFormats", [])
            table_conditional_formats = _filter_conditional_formats_for_table(conditional_formats, table_metadata)
            
            # Get filters
            basic_filter = sheet_metadata.get("sheets", [])[0].get("basicFilter", {})
            table_filters = _filter_basic_filter_for_table(basic_filter, table_metadata)
            
            # Format the response
            formatted_metadata = {
                "table_name": validated_table_name,
                "table_id": table_id,
                "spreadsheet_name": spreadsheet_name,
                "sheet_name": sheet_name,
                "dimensions": {
                    "column_count": table_metadata.get("column_count"),
                    "row_count": table_metadata.get("row_count"),
                    "frozen_rows": frozen_rows,
                    "frozen_columns": frozen_columns
                },
                "range": {
                    "start_row": table_metadata.get("start_row"),
                    "end_row": table_metadata.get("end_row"),
                    "start_column": table_metadata.get("start_col"),
                    "end_column": table_metadata.get("end_col")
                },
                "range_notation": table_metadata.get("range_notation"),
                "columns": columns,
                "column_dimensions": column_dimensions,
                "header_row": {
                    "index": table_metadata.get("start_row"),
                    "values": sample_data[0] if sample_data else None
                },
                "modification_info": {
                    "last_modified": spreadsheet_metadata.get("modifiedTime"),
                    "last_modified_by": spreadsheet_metadata.get("lastModifyingUser", {}).get("displayName")
                }
            }
            
            # Add optional data based on parameters and exclusions
            if not exclude_metadata_types or "sample_data" not in exclude_metadata_types:
                if include_sample_data:
                    formatted_metadata["sample_data"] = sample_data[1:] if sample_data else []
            
            if not exclude_metadata_types or "formatting" not in exclude_metadata_types:
                if include_formatting:
                    formatted_metadata["formatting"] = formatting_data
            
            if not exclude_metadata_types or "statistics" not in exclude_metadata_types:
                if include_statistics:
                    formatted_metadata["statistics"] = statistics
            
            if not exclude_metadata_types or "merges" not in exclude_metadata_types:
                formatted_metadata["merges"] = table_merges
            
            if not exclude_metadata_types or "conditional_formatting" not in exclude_metadata_types:
                formatted_metadata["conditional_formatting"] = table_conditional_formats
            
            if not exclude_metadata_types or "filters" not in exclude_metadata_types:
                formatted_metadata["filters"] = table_filters
            
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
    spreadsheet_name: str,
    sheet_props: Dict,
    spreadsheet_metadata: Dict,
    include_sample_data: bool = False,
    include_formulas: bool = False,
    include_formatting: bool = False,
    include_statistics: bool = False,
    max_sample_rows: int = 5,
    specific_columns: List[str] = None,
    exclude_metadata_types: List[str] = None
) -> str:
    """
    Get metadata for all tables in a sheet with enhanced information.
    
    Args:
        sheets_service: Google Sheets service
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet
        sheet_name: Name of the sheet
        spreadsheet_name: Name of the spreadsheet
        sheet_props: Sheet properties
        spreadsheet_metadata: Spreadsheet metadata
        include_sample_data: Whether to include sample data
        include_formulas: Whether to include formulas
        include_formatting: Whether to include formatting
        include_statistics: Whether to include statistics
        max_sample_rows: Maximum sample rows
        specific_columns: Specific columns to include
        exclude_metadata_types: Metadata types to exclude
    
    Returns:
        str: JSON-formatted string containing all tables metadata
    """
    try:
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets(tables,merges,protectedRanges,basicFilter,conditionalFormats)"
        ).execute()
        
        all_tables = []
        total_tables = 0
        
        # Get frozen dimensions
        grid_properties = sheet_props.get("gridProperties", {})
        frozen_rows = grid_properties.get("frozenRowCount", 0)
        frozen_columns = grid_properties.get("frozenColumnCount", 0)
        
        for sheet in result.get("sheets", []):
            if sheet.get("properties", {}).get("sheetId") == sheet_id:
                tables = sheet.get("tables", [])
                total_tables = len(tables)
                
                # Get sheet-wide metadata
                merges = sheet.get("merges", [])
                conditional_formats = sheet.get("conditionalFormats", [])
                basic_filter = sheet.get("basicFilter", {})
                
                for table in tables:
                    table_id = table.get("tableId")
                    table_name = table.get("displayName") or table.get("name") or f"Table{table_id}"
                    
                    # Get table range
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
                        if specific_columns and col_prop.get("columnName") not in specific_columns:
                            continue
                            
                        column_info = {
                            "name": col_prop.get("columnName", f"Column {i+1}"),
                            "type": col_prop.get("columnType", "TEXT"),
                            "index": i,
                            "width": col_prop.get("pixelSize")
                        }
                        
                        # Add data validation info
                        data_validation = col_prop.get("dataValidationRule", {})
                        if data_validation:
                            column_info["validation"] = data_validation
                            if data_validation.get("condition", {}).get("type") == "ONE_OF_LIST":
                                column_info["type"] = "DROPDOWN"
                                column_info["dropdown_options"] = [
                                    v.get("userEnteredValue", "") 
                                    for v in data_validation.get("condition", {}).get("values", [])
                                ]
                        
                        columns.append(column_info)
                    
                    # Get sample data if requested
                    sample_data = None
                    if include_sample_data:
                        range_notation = f"{sheet_name}!{column_index_to_letter(start_col)}{start_row + 1}:{column_index_to_letter(end_col - 1)}{end_row}"
                        data_response = sheets_service.spreadsheets().values().get(
                            spreadsheetId=spreadsheet_id,
                            range=range_notation,
                            valueRenderOption="UNFORMATTED_VALUE" if not include_formulas else "FORMULA"
                        ).execute()
                        sample_data = data_response.get("values", [])[:max_sample_rows]
                    
                    # Calculate statistics if requested
                    statistics = None
                    if include_statistics and sample_data:
                        statistics = _calculate_statistics(sample_data)
                    
                    # Filter metadata for table range
                    table_merges = _filter_merges_for_table(merges, {
                        "start_row": start_row,
                        "end_row": end_row,
                        "start_col": start_col,
                        "end_col": end_col
                    })
                    
                    table_conditional_formats = _filter_conditional_formats_for_table(
                        conditional_formats,
                        {
                            "start_row": start_row,
                            "end_row": end_row,
                            "start_col": start_col,
                            "end_col": end_col
                        }
                    )
                    
                    table_filters = _filter_basic_filter_for_table(
                        basic_filter,
                        {
                            "start_row": start_row,
                            "end_row": end_row,
                            "start_col": start_col,
                            "end_col": end_col
                        }
                    )
                    
                    table_info = {
                        "table_id": table_id,
                        "table_name": table_name,
                        "dimensions": {
                            "column_count": column_count,
                            "row_count": row_count,
                            "frozen_rows": frozen_rows,
                            "frozen_columns": frozen_columns
                        },
                        "range": {
                            "start_row": start_row,
                            "end_row": end_row,
                            "start_column": start_col,
                            "end_column": end_col
                        },
                        "range_notation": f"{column_index_to_letter(start_col)}{start_row + 1}:{column_index_to_letter(end_col - 1)}{end_row}",
                        "columns": columns,
                        "header_row": {
                            "index": start_row,
                            "values": sample_data[0] if sample_data else None
                        },
                        "modification_info": {
                            "last_modified": spreadsheet_metadata.get("modifiedTime"),
                            "last_modified_by": spreadsheet_metadata.get("lastModifyingUser", {}).get("displayName")
                        }
                    }
                    
                    # Add optional data based on parameters and exclusions
                    if not exclude_metadata_types or "sample_data" not in exclude_metadata_types:
                        if include_sample_data:
                            table_info["sample_data"] = sample_data[1:] if sample_data else []
                    
                    if not exclude_metadata_types or "statistics" not in exclude_metadata_types:
                        if include_statistics:
                            table_info["statistics"] = statistics
                    
                    if not exclude_metadata_types or "merges" not in exclude_metadata_types:
                        table_info["merges"] = table_merges
                    
                    if not exclude_metadata_types or "conditional_formatting" not in exclude_metadata_types:
                        table_info["conditional_formatting"] = table_conditional_formats
                    
                    if not exclude_metadata_types or "filters" not in exclude_metadata_types:
                        table_info["filters"] = table_filters
                    
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

def _calculate_statistics(data: List[List[Any]]) -> Dict[str, Any]:
    """Calculate statistics for table data."""
    if not data:
        return {}
    
    header = data[0]
    data_rows = data[1:] if len(data) > 1 else []
    
    stats = {
        "total_rows": len(data_rows),
        "columns": []
    }
    
    for col_idx, col_name in enumerate(header):
        col_stats = {
            "name": col_name,
            "empty_cells": 0,
            "data_type_distribution": {},
            "unique_values": set()
        }
        
        for row in data_rows:
            if col_idx >= len(row) or row[col_idx] is None or row[col_idx] == "":
                col_stats["empty_cells"] += 1
            else:
                value = row[col_idx]
                data_type = type(value).__name__
                col_stats["data_type_distribution"][data_type] = col_stats["data_type_distribution"].get(data_type, 0) + 1
                col_stats["unique_values"].add(str(value))
        
        col_stats["unique_values"] = len(col_stats["unique_values"])
        col_stats["filled_cells"] = len(data_rows) - col_stats["empty_cells"]
        
        stats["columns"].append(col_stats)
    
    return stats

def _filter_merges_for_table(merges: List[Dict], table_metadata: Dict) -> List[Dict]:
    """Filter merged ranges that overlap with the table."""
    table_merges = []
    
    start_row = table_metadata.get("start_row", 0)
    end_row = table_metadata.get("end_row", 0)
    start_col = table_metadata.get("start_col", 0)
    end_col = table_metadata.get("end_col", 0)
    
    for merge in merges:
        merge_range = merge.get("range", {})
        merge_start_row = merge_range.get("startRowIndex", 0)
        merge_end_row = merge_range.get("endRowIndex", 0)
        merge_start_col = merge_range.get("startColumnIndex", 0)
        merge_end_col = merge_range.get("endColumnIndex", 0)
        
        # Check if merge range overlaps with table range
        if (merge_start_row < end_row and merge_end_row > start_row and
            merge_start_col < end_col and merge_end_col > start_col):
            table_merges.append({
                "start_row": merge_start_row,
                "end_row": merge_end_row,
                "start_column": merge_start_col,
                "end_column": merge_end_col,
                "range_notation": f"{column_index_to_letter(merge_start_col)}{merge_start_row + 1}:{column_index_to_letter(merge_end_col - 1)}{merge_end_row}"
            })
    
    return table_merges

def _filter_conditional_formats_for_table(conditional_formats: List[Dict], table_metadata: Dict) -> List[Dict]:
    """Filter conditional formats that apply to the table."""
    table_formats = []
    
    start_row = table_metadata.get("start_row", 0)
    end_row = table_metadata.get("end_row", 0)
    start_col = table_metadata.get("start_col", 0)
    end_col = table_metadata.get("end_col", 0)
    
    for cf in conditional_formats:
        ranges = cf.get("ranges", [])
        for range_def in ranges:
            range_start_row = range_def.get("startRowIndex", 0)
            range_end_row = range_def.get("endRowIndex", 0)
            range_start_col = range_def.get("startColumnIndex", 0)
            range_end_col = range_def.get("endColumnIndex", 0)
            
            # Check if conditional format range overlaps with table range
            if (range_start_row < end_row and range_end_row > start_row and
                range_start_col < end_col and range_end_col > start_col):
                table_formats.append({
                    "type": cf.get("type"),
                    "format": cf.get("format"),
                    "range": {
                        "start_row": range_start_row,
                        "end_row": range_end_row,
                        "start_column": range_start_col,
                        "end_column": range_end_col,
                        "range_notation": f"{column_index_to_letter(range_start_col)}{range_start_row + 1}:{column_index_to_letter(range_end_col - 1)}{range_end_row}"
                    }
                })
    
    return table_formats

def _filter_basic_filter_for_table(basic_filter: Dict, table_metadata: Dict) -> Optional[Dict]:
    """Filter basic filter that applies to the table."""
    if not basic_filter:
        return None
    
    filter_range = basic_filter.get("range", {})
    filter_start_row = filter_range.get("startRowIndex", 0)
    filter_end_row = filter_range.get("endRowIndex", 0)
    filter_start_col = filter_range.get("startColumnIndex", 0)
    filter_end_col = filter_range.get("endColumnIndex", 0)
    
    start_row = table_metadata.get("start_row", 0)
    end_row = table_metadata.get("end_row", 0)
    start_col = table_metadata.get("start_col", 0)
    end_col = table_metadata.get("end_col", 0)
    
    # Check if filter range overlaps with table range
    if (filter_start_row < end_row and filter_end_row > start_row and
        filter_start_col < end_col and filter_end_col > start_col):
        return {
            "range": {
                "start_row": filter_start_row,
                "end_row": filter_end_row,
                "start_column": filter_start_col,
                "end_column": filter_end_col,
                "range_notation": f"{column_index_to_letter(filter_start_col)}{filter_start_row + 1}:{column_index_to_letter(filter_end_col - 1)}{filter_end_row}"
            },
            "criteria": basic_filter.get("criteria", {}),
            "sort_specs": basic_filter.get("sortSpecs", [])
        }
    
    return None