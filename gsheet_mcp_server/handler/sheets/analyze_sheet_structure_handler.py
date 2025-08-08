from typing import Dict, Any, List, Optional
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response


def analyze_sheet_structure_simple(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str
) -> Dict[str, Any]:
    """
    Simple analysis of a sheet structure - quick overview of elements and data.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet to analyze
    
    Returns:
        Dictionary with simple sheet structure and data overview
    """
    try:
        # Get comprehensive spreadsheet data including values
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.charts,sheets.tables,sheets.slicers,sheets.developerMetadata,sheets.drawings,sheets.data"
        ).execute()
        
        sheets = result.get('sheets', [])
        
        # Find the specific sheet
        target_sheet = None
        for sheet in sheets:
            props = sheet.get('properties', {})
            if props.get('title') == sheet_name:
                target_sheet = sheet
                break
        
        if not target_sheet:
            raise RuntimeError(f"Sheet '{sheet_name}' not found in spreadsheet")
        
        return process_simple_sheet_analysis(target_sheet, sheets_service, spreadsheet_id, sheet_name)
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Google Sheets API error: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error analyzing sheet structure: {str(error)}")


def process_simple_sheet_analysis(sheet: Dict[str, Any], sheets_service, spreadsheet_id: str, sheet_name: str) -> Dict[str, Any]:
    """
    Process simple analysis for a single sheet - overview of structure and data.
    
    Args:
        sheet: Raw sheet data from API
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet
    
    Returns:
        Simple sheet structure and data overview
    """
    props = sheet.get('properties', {})
    grid_props = props.get('gridProperties', {})
    
    # Basic sheet info
    sheet_info = {
        "name": props.get('title'),
        "hidden": props.get('hidden', False),
        "grid_size": f"{grid_props.get('rowCount', 0)} rows × {grid_props.get('columnCount', 0)} columns"
    }
    
    # Get structured elements first
    tables = sheet.get('tables', [])
    charts = sheet.get('charts', [])
    slicers = sheet.get('slicers', [])
    drawings = sheet.get('drawings', [])
    dev_metadata = sheet.get('developerMetadata', [])
    
    # Create structured element ranges for exclusion
    structured_ranges = []
    
    # Add table ranges
    for table in tables:
        table_range = table.get('range', {})
        if table_range:
            start_row = table_range.get('startRowIndex', 0) + 1
            end_row = table_range.get('endRowIndex', 0)
            start_col = table_range.get('startColumnIndex', 0) + 1
            end_col = table_range.get('endColumnIndex', 0)
            structured_ranges.append({
                "type": "table",
                "name": table.get('displayName', table.get('name', 'Unknown')),
                "start_row": start_row,
                "end_row": end_row,
                "start_col": start_col,
                "end_col": end_col,
                "range": f"{chr(64 + start_col)}{start_row}:{chr(64 + end_col)}{end_row}"
            })
    
    # Add chart ranges (approximate based on position)
    for chart in charts:
        position = chart.get('position', {})
        if position:
            structured_ranges.append({
                "type": "chart",
                "id": chart.get('chartId', 'Unknown'),
                "position": position
            })
    
    # Add slicer ranges
    for slicer in slicers:
        position = slicer.get('position', {})
        if position:
            structured_ranges.append({
                "type": "slicer",
                "id": slicer.get('slicerId', 'Unknown'),
                "position": position
            })
    
    # Add drawing ranges
    for drawing in drawings:
        position = drawing.get('position', {})
        if position:
            structured_ranges.append({
                "type": "drawing",
                "id": drawing.get('drawingId', 'Unknown'),
                "position": position
            })
    
    # Get sheet data to analyze content
    try:
        data_response = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A1:Z1000"  # Get first 1000 rows and 26 columns
        ).execute()
        
        values = data_response.get('values', [])
        data_analysis = analyze_sheet_data_separated(values, structured_ranges)
    except Exception as e:
        data_analysis = {
            "structured_data": [],
            "unstructured_data": [],
            "data_summary": {
                "total_structured_rows": 0,
                "total_unstructured_rows": 0,
                "total_columns_with_data": 0,
                "structured_areas": [],
                "unstructured_areas": []
            }
        }
    
    # Tables overview
    tables_overview = {
        "count": len(tables),
        "items": []
    }
    for table in tables:
        table_info = {
            "name": table.get('displayName', table.get('name', 'Unnamed')),
            "range": table.get('range', 'Unknown'),
            "size": f"{len(table.get('columns', []))} columns × {len(table.get('rows', []))} rows"
        }
        tables_overview["items"].append(table_info)
    
    # Charts overview
    charts_overview = {
        "count": len(charts),
        "items": []
    }
    for chart in charts:
        chart_info = {
            "id": chart.get('chartId', 'Unknown'),
            "position": chart.get('position', {}).get('overlayPosition', {}).get('anchorCell', {}).get('sheetId', 'Unknown')
        }
        charts_overview["items"].append(chart_info)
    
    # Slicers overview
    slicers_overview = {
        "count": len(slicers),
        "items": []
    }
    for slicer in slicers:
        slicer_info = {
            "id": slicer.get('slicerId', 'Unknown'),
            "position": slicer.get('position', {}).get('overlayPosition', {}).get('anchorCell', {}).get('sheetId', 'Unknown')
        }
        slicers_overview["items"].append(slicer_info)
    
    # Drawings overview
    drawings_overview = {
        "count": len(drawings),
        "items": []
    }
    for drawing in drawings:
        drawing_info = {
            "id": drawing.get('drawingId', 'Unknown'),
            "position": drawing.get('position', {}).get('overlayPosition', {}).get('anchorCell', {}).get('sheetId', 'Unknown')
        }
        drawings_overview["items"].append(drawing_info)
    
    # Developer metadata overview
    metadata_overview = {
        "count": len(dev_metadata),
        "items": []
    }
    for metadata in dev_metadata:
        metadata_info = {
            "key": metadata.get('metadataKey', 'Unknown'),
            "value": metadata.get('metadataValue', 'Unknown')
        }
        metadata_overview["items"].append(metadata_info)
    
    # Calculate simple summary
    total_structured_elements = len(tables) + len(charts) + len(slicers) + len(drawings) + len(dev_metadata)
    total_unstructured_data = len(data_analysis["unstructured_data"])
    
    sheet_type = "EMPTY" if total_structured_elements == 0 and total_unstructured_data == 0 else "DATA_TABLE" if len(tables) > 0 else "DATA_SHEET" if total_unstructured_data > 0 else "VISUAL"
    
    summary = {
        "total_structured_elements": total_structured_elements,
        "total_unstructured_data_areas": total_unstructured_data,
        "sheet_type": sheet_type,
        "has_frozen_panes": grid_props.get('frozenRowCount', 0) > 0 or grid_props.get('frozenColumnCount', 0) > 0,
        "element_breakdown": {
            "tables": len(tables),
            "charts": len(charts),
            "slicers": len(slicers),
            "drawings": len(drawings),
            "metadata": len(dev_metadata)
        },
        "data_content": data_analysis["data_summary"]
    }
    
    return {
        "sheet_info": sheet_info,
        "structured_elements": {
            "tables": tables_overview,
            "charts": charts_overview,
            "slicers": slicers_overview,
            "drawings": drawings_overview,
            "developer_metadata": metadata_overview
        },
        "unstructured_data": data_analysis["unstructured_data"],
        "summary": summary
    }


def analyze_sheet_data_separated(values: List[List[Any]], structured_ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the actual data content in the sheet, separating structured from unstructured data.
    
    Args:
        values: 2D array of cell values from the sheet
        structured_ranges: List of structured element ranges to exclude
    
    Returns:
        Analysis of structured and unstructured data
    """
    if not values:
        return {
            "structured_data": [],
            "unstructured_data": [],
            "data_summary": {
                "total_structured_rows": 0,
                "total_unstructured_rows": 0,
                "total_columns_with_data": 0,
                "structured_areas": [],
                "unstructured_areas": []
            }
        }
    
    # Find data ranges, properly excluding structured elements
    unstructured_data = []
    structured_data = []
    
    # Create a set of cells that are part of structured elements for quick lookup
    structured_cells = set()
    for struct_range in structured_ranges:
        if struct_range["type"] == "table":
            for row in range(struct_range["start_row"], struct_range["end_row"] + 1):
                for col in range(struct_range["start_col"], struct_range["end_col"] + 1):
                    structured_cells.add((row, col))
    
    # Analyze each row
    for row_idx, row in enumerate(values):
        if row:  # Row has some data
            # Find start and end of data in this row
            start_col = 0
            end_col = len(row) - 1
            
            # Trim empty cells from start
            while start_col < len(row) and (row[start_col] == '' or row[start_col] is None):
                start_col += 1
            
            # Trim empty cells from end
            while end_col >= start_col and (row[end_col] == '' or row[end_col] is None):
                end_col -= 1
            
            if start_col <= end_col:  # Found data in this row
                row_num = row_idx + 1
                
                # Check each cell in the row to see if it's structured or unstructured
                current_start = start_col
                current_end = start_col
                is_current_structured = (row_num, start_col + 1) in structured_cells
                
                for col_idx in range(start_col + 1, end_col + 1):
                    cell_is_structured = (row_num, col_idx + 1) in structured_cells
                    
                    if cell_is_structured == is_current_structured:
                        # Same type, extend current range
                        current_end = col_idx
                    else:
                        # Different type, save current range and start new one
                        if current_start <= current_end:
                            data_range = {
                                "row": row_num,
                                "start_column": chr(65 + current_start),
                                "end_column": chr(65 + current_end),
                                "range": f"{chr(65 + current_start)}{row_num}:{chr(65 + current_end)}{row_num}",
                                "data_count": current_end - current_start + 1
                            }
                            
                            if is_current_structured:
                                structured_data.append(data_range)
                            else:
                                unstructured_data.append(data_range)
                        
                        # Start new range
                        current_start = col_idx
                        current_end = col_idx
                        is_current_structured = cell_is_structured
                
                # Save the last range
                if current_start <= current_end:
                    data_range = {
                        "row": row_num,
                        "start_column": chr(65 + current_start),
                        "end_column": chr(65 + current_end),
                        "range": f"{chr(65 + current_start)}{row_num}:{chr(65 + current_end)}{row_num}",
                        "data_count": current_end - current_start + 1
                    }
                    
                    if is_current_structured:
                        structured_data.append(data_range)
                    else:
                        unstructured_data.append(data_range)
    
    # Group unstructured data into areas
    unstructured_areas = group_data_into_areas(unstructured_data)
    structured_areas = group_data_into_areas(structured_data)
    
    # Calculate summary
    total_structured_rows = len(structured_data)
    total_unstructured_rows = len(unstructured_data)
    total_columns_with_data = max([
        max([range_info["data_count"] for range_info in structured_data]) if structured_data else 0,
        max([range_info["data_count"] for range_info in unstructured_data]) if unstructured_data else 0
    ])
    
    return {
        "structured_data": structured_data,
        "unstructured_data": unstructured_data,
        "data_summary": {
            "total_structured_rows": total_structured_rows,
            "total_unstructured_rows": total_unstructured_rows,
            "total_columns_with_data": total_columns_with_data,
            "structured_areas": structured_areas,
            "unstructured_areas": unstructured_areas
        }
    }


def group_data_into_areas(data_ranges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group consecutive data ranges into areas following standard spreadsheet range rules.
    
    Args:
        data_ranges: List of data range dictionaries
    
    Returns:
        List of grouped data areas with proper ranges
    """
    if not data_ranges:
        return []
    
    # Sort by row and column for proper grouping
    sorted_ranges = sorted(data_ranges, key=lambda x: (x["row"], ord(x["start_column"])))
    
    areas = []
    current_area = None
    
    for data_range in sorted_ranges:
        if not current_area:
            # Start new area
            current_area = {
                "start_row": data_range["row"],
                "end_row": data_range["row"],
                "start_column": data_range["start_column"],
                "end_column": data_range["end_column"],
                "range": data_range["range"],
                "data_count": data_range["data_count"]
            }
        elif (data_range["row"] == current_area["end_row"] + 1 and 
              data_range["start_column"] == current_area["start_column"] and
              data_range["end_column"] == current_area["end_column"]):
            # Consecutive row with same column range, extend area
            current_area["end_row"] = data_range["row"]
            current_area["range"] = f"{current_area['start_column']}{current_area['start_row']}:{current_area['end_column']}{current_area['end_row']}"
            current_area["data_count"] += data_range["data_count"]
        elif (data_range["row"] == current_area["end_row"] and
              data_range["start_column"] == chr(ord(current_area["end_column"]) + 1)):
            # Same row, consecutive column, extend area
            current_area["end_column"] = data_range["end_column"]
            current_area["range"] = f"{current_area['start_column']}{current_area['start_row']}:{current_area['end_column']}{current_area['end_row']}"
            current_area["data_count"] += data_range["data_count"]
        else:
            # Non-consecutive, start new area
            areas.append(current_area)
            current_area = {
                "start_row": data_range["row"],
                "end_row": data_range["row"],
                "start_column": data_range["start_column"],
                "end_column": data_range["end_column"],
                "range": data_range["range"],
                "data_count": data_range["data_count"]
            }
    
    if current_area:
        areas.append(current_area)
    
    return areas


def analyze_sheet_structure_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str
) -> str:
    """
    Handler for analyzing sheet structure - simplified overview with separated data detection.
    """
    try:
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        
        # Perform simple analysis
        analysis = analyze_sheet_structure_simple(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name
        )
        
        result = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "analysis": analysis,
            "message": f"Successfully analyzed sheet structure '{sheet_name}' in '{spreadsheet_name}'"
        }
        
        return compact_json_response(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "message": f"Error analyzing sheet structure: {str(e)}"
        }
        return compact_json_response(error_result)
