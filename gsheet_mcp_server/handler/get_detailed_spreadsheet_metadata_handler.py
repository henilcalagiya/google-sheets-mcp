from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response


def get_spreadsheet_metadata(
    sheets_service,
    spreadsheet_id: str
) -> Dict[str, Any]:
    """
    Get metadata about a spreadsheet focusing on spreadsheet-level information.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
    
    Returns:
        Dict containing spreadsheet-level metadata with basic sheet information
    """
    
    try:
        # Get spreadsheet metadata with minimal sheet details to reduce response size
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="spreadsheetId,properties,namedRanges,developerMetadata,sheets(properties)"
        ).execute()
        
        # Extract basic spreadsheet-level metadata
        sheets = result.get('sheets', [])
        sheet_names = []
        hidden_count = 0
        
        for sheet in sheets:
            props = sheet.get('properties', {})
            sheet_names.append(props.get('title', ''))
            if props.get('hidden', False):
                hidden_count += 1
        
        spreadsheet_metadata = {
            "spreadsheet_id": result.get('spreadsheetId'),
            "properties": result.get('properties', {}),
            "named_ranges": result.get('namedRanges', []),
            "developer_metadata": result.get('developerMetadata', []),
            "total_sheets": len(sheets),
            "hidden_sheets": hidden_count,
            "visible_sheets": len(sheets) - hidden_count,
            "sheet_names": sheet_names
        }
        
        return spreadsheet_metadata
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error getting detailed spreadsheet metadata: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error getting detailed spreadsheet metadata: {error}")


def process_sheet_metadata(sheet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process metadata for a single sheet including all embedded objects.
    
    Args:
        sheet: Raw sheet data from API
    
    Returns:
        Processed sheet metadata
    """
    props = sheet.get('properties', {})
    
    sheet_metadata = {
        "sheet_id": props.get('sheetId'),
        "title": props.get('title'),
        "index": props.get('index'),
        "sheet_type": props.get('sheetType', 'GRID'),
        "hidden": props.get('hidden', False),
        "tab_color": props.get('tabColor', {}),
        "right_to_left": props.get('rightToLeft', False),
        "grid_properties": process_grid_properties(props.get('gridProperties', {})),
        "charts": process_charts(sheet.get('charts', [])),
        "tables": process_tables(sheet.get('tables', [])),
        "slicers": process_slicers(sheet.get('slicers', [])),
        "drawings": process_drawings(sheet.get('drawings', [])),
        "developer_metadata": process_developer_metadata(sheet.get('developerMetadata', []))
    }
    
    return sheet_metadata


def process_grid_properties(grid_props: Dict[str, Any]) -> Dict[str, Any]:
    """Process grid properties of a sheet."""
    return {
        "row_count": grid_props.get('rowCount', 0),
        "column_count": grid_props.get('columnCount', 0),
        "frozen_row_count": grid_props.get('frozenRowCount', 0),
        "frozen_column_count": grid_props.get('frozenColumnCount', 0),
        "hide_gridlines": grid_props.get('hideGridlines', False),
        "row_group_control_after": grid_props.get('rowGroupControlAfter', False),
        "column_group_control_after": grid_props.get('columnGroupControlAfter', False)
    }


def process_charts(charts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process charts in a sheet."""
    processed_charts = []
    
    for chart in charts:
        chart_spec = chart.get('spec', {})
        basic_chart = chart_spec.get('basicChart', {})
        pie_chart = chart_spec.get('pieChart', {})
        bubble_chart = chart_spec.get('bubbleChart', {})
        candlestick_chart = chart_spec.get('candlestickChart', {})
        org_chart = chart_spec.get('orgChart', {})
        histogram_chart = chart_spec.get('histogramChart', {})
        waterfall_chart = chart_spec.get('waterfallChart', {})
        treemap_chart = chart_spec.get('treemapChart', {})
        
        chart_info = {
            "chart_id": chart.get('chartId'),
            "position": chart.get('position', {}),
            "chart_type": "UNKNOWN"
        }
        
        # Determine chart type
        if basic_chart:
            chart_info["chart_type"] = basic_chart.get('chartType', 'UNKNOWN')
            chart_info["chart_spec"] = {
                "axis": basic_chart.get('axis', []),
                "domains": basic_chart.get('domains', []),
                "series": basic_chart.get('series', []),
                "legend_position": basic_chart.get('legendPosition', 'UNSPECIFIED_LEGEND_POSITION')
            }
        elif pie_chart:
            chart_info["chart_type"] = "PIE"
            chart_info["chart_spec"] = {
                "domain": pie_chart.get('domain', {}),
                "series": pie_chart.get('series', {}),
                "legend_position": pie_chart.get('legendPosition', 'UNSPECIFIED_LEGEND_POSITION')
            }
        elif bubble_chart:
            chart_info["chart_type"] = "BUBBLE"
            chart_info["chart_spec"] = {
                "domain": bubble_chart.get('domain', {}),
                "series": bubble_chart.get('series', [])
            }
        elif candlestick_chart:
            chart_info["chart_type"] = "CANDLESTICK"
            chart_info["chart_spec"] = {
                "domain": candlestick_chart.get('domain', {}),
                "series": candlestick_chart.get('series', [])
            }
        elif org_chart:
            chart_info["chart_type"] = "ORG_CHART"
            chart_info["chart_spec"] = {
                "node_size": org_chart.get('nodeSize', 'UNSPECIFIED_NODE_SIZE'),
                "parent_labels": org_chart.get('parentLabels', 'UNSPECIFIED_PARENT_LABELS'),
                "selected_node_color": org_chart.get('selectedNodeColor', {}),
                "tooltips": org_chart.get('tooltips', 'UNSPECIFIED_TOOLTIPS')
            }
        elif histogram_chart:
            chart_info["chart_type"] = "HISTOGRAM"
            chart_info["chart_spec"] = {
                "series": histogram_chart.get('series', []),
                "legend_position": histogram_chart.get('legendPosition', 'UNSPECIFIED_LEGEND_POSITION'),
                "show_series_percentages": histogram_chart.get('showSeriesPercentages', False),
                "show_series_values": histogram_chart.get('showSeriesValues', False)
            }
        elif waterfall_chart:
            chart_info["chart_type"] = "WATERFALL"
            chart_info["chart_spec"] = {
                "domain": waterfall_chart.get('domain', {}),
                "series": waterfall_chart.get('series', []),
                "first_value_is_total": waterfall_chart.get('firstValueIsTotal', False),
                "connector_line_style": waterfall_chart.get('connectorLineStyle', {})
            }
        elif treemap_chart:
            chart_info["chart_type"] = "TREEMAP"
            chart_info["chart_spec"] = {
                "domain": treemap_chart.get('domain', {}),
                "series": treemap_chart.get('series', {}),
                "header_color": treemap_chart.get('headerColor', {}),
                "max_depth": treemap_chart.get('maxDepth', 0)
            }
        
        processed_charts.append(chart_info)
    
    return {
        "total_charts": len(processed_charts),
        "charts": processed_charts,
        "chart_types": [chart["chart_type"] for chart in processed_charts]
    }


def process_tables(tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process regular tables in a sheet."""
    processed_tables = []
    
    for table in tables:
        table_range = table.get('range', {})
        start_row = table_range.get('startRowIndex', 0)
        end_row = table_range.get('endRowIndex', 0)
        start_col = table_range.get('startColumnIndex', 0)
        end_col = table_range.get('endColumnIndex', 0)
        
        # Calculate actual row and column counts from range
        actual_row_count = end_row - start_row
        actual_column_count = end_col - start_col
        
        table_info = {
            "table_id": table.get('tableId'),
            "table_name": table.get('name', 'Unknown'),
            "range": table_range,
            "row_count": actual_row_count,
            "column_count": actual_column_count,
            "start_row": start_row,
            "end_row": end_row,
            "start_col": start_col,
            "end_col": end_col,
            "column_properties": table.get('columnProperties', []),
            "rows_properties": table.get('rowsProperties', [])
        }
        processed_tables.append(table_info)
    
    return {
        "total_tables": len(processed_tables),
        "tables": processed_tables
    }





def process_slicers(slicers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process slicers in a sheet."""
    processed_slicers = []
    
    for slicer in slicers:
        slicer_info = {
            "slicer_id": slicer.get('slicerId'),
            "position": slicer.get('position', {}),
            "spec": slicer.get('spec', {}),
            "data_source_id": slicer.get('dataSourceId'),
            "column_index": slicer.get('columnIndex', 0),
            "start_row_index": slicer.get('startRowIndex', 0),
            "start_column_index": slicer.get('startColumnIndex', 0),
            "end_row_index": slicer.get('endRowIndex', 0),
            "end_column_index": slicer.get('endColumnIndex', 0)
        }
        processed_slicers.append(slicer_info)
    
    return {
        "total_slicers": len(processed_slicers),
        "slicers": processed_slicers
    }


def process_drawings(drawings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process drawings in a sheet."""
    processed_drawings = []
    
    for drawing in drawings:
        drawing_info = {
            "drawing_id": drawing.get('drawingId'),
            "position": drawing.get('position', {}),
            "shape": drawing.get('shape', {}),
            "image": drawing.get('image', {}),
            "line": drawing.get('line', {}),
            "word_art": drawing.get('wordArt', {}),
            "chart": drawing.get('chart', {})
        }
        processed_drawings.append(drawing_info)
    
    return {
        "total_drawings": len(processed_drawings),
        "drawings": processed_drawings
    }





def process_developer_metadata(developer_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process developer metadata."""
    processed_metadata = []
    
    for metadata in developer_metadata:
        metadata_info = {
            "metadata_id": metadata.get('metadataId'),
            "metadata_key": metadata.get('metadataKey', ''),
            "metadata_value": metadata.get('metadataValue', ''),
            "visibility": metadata.get('visibility', 'DOCUMENT')
        }
        processed_metadata.append(metadata_info)
    
    return {
        "total_metadata": len(processed_metadata),
        "metadata": processed_metadata
    }





def get_spreadsheet_metadata_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str
) -> str:
    """
    Handler for getting spreadsheet metadata.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        spreadsheet_name: Name of the spreadsheet
    
    Returns:
        Compact JSON string containing spreadsheet metadata
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    try:
        metadata = get_spreadsheet_metadata(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id
        )
        
        response = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "metadata": metadata,
            "message": f"Successfully retrieved metadata for spreadsheet '{spreadsheet_name}'"
        }
        
        # Return compact JSON string (no newlines, no spaces)
        return compact_json_response(response)
            
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error getting spreadsheet metadata: {str(e)}"
        }) 