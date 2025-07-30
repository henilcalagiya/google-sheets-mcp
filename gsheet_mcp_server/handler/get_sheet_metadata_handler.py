from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response


def get_detailed_sheet_metadata(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str
) -> Dict[str, Any]:
    """
    Get detailed metadata for a specific sheet including charts, tables, slicers, and drawings.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the specific sheet to get metadata for
    
    Returns:
        Dict containing detailed sheet metadata
    """
    
    try:
        # Get comprehensive spreadsheet metadata with verified working fields
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.charts,sheets.tables,sheets.slicers,sheets.developerMetadata,sheets.drawings"
        ).execute()
        
        sheets = result.get('sheets', [])
        
        # Find the specific sheet
        for sheet in sheets:
            props = sheet.get('properties', {})
            if props.get('title') == sheet_name:
                return process_detailed_sheet_metadata(sheet)
        
        # If sheet not found, raise error
        raise RuntimeError(f"Sheet '{sheet_name}' not found in spreadsheet")
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Google Sheets API error: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error getting detailed sheet metadata: {str(error)}")


def process_detailed_sheet_metadata(sheet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process detailed metadata for a single sheet.
    
    Args:
        sheet: Raw sheet data from API
    
    Returns:
        Processed sheet metadata
    """
    props = sheet.get('properties', {})
    
    sheet_info = {
        "sheet_id": props.get('sheetId'),
        "title": props.get('title'),
        "index": props.get('index'),
        "hidden": props.get('hidden', False),
        "tab_color": props.get('tabColor', {}),
        "right_to_left": props.get('rightToLeft', False),
        "sheet_type": props.get('sheetType', 'GRID'),
        "grid_properties": process_grid_properties(props.get('gridProperties', {})),
        "charts": process_charts(sheet.get('charts', [])),
        "tables": process_tables(sheet.get('tables', [])),
        "slicers": process_slicers(sheet.get('slicers', [])),
        "drawings": process_drawings(sheet.get('drawings', [])),
        "developer_metadata": process_developer_metadata(sheet.get('developerMetadata', []))
    }
    
    return sheet_info


def process_grid_properties(grid_props: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process grid properties for a sheet.
    
    Args:
        grid_props: Raw grid properties from API
    
    Returns:
        Processed grid properties
    """
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
    """
    Process charts data for a sheet.
    
    Args:
        charts: List of charts from API
    
    Returns:
        Processed charts data
    """
    total_charts = len(charts)
    chart_ids = []
    chart_types = []
    chart_titles = []
    chart_ranges = []
    
    for chart in charts:
        chart_id = chart.get('chartId')
        chart_ids.append(chart_id)
        
        spec = chart.get('spec', {})
        
        # Get chart type - handle all chart types
        chart_type = 'UNKNOWN'
        if spec.get('basicChart'):
            chart_type = spec['basicChart'].get('chartType', 'BASIC_CHART')
        elif spec.get('pieChart'):
            chart_type = 'PIE_CHART'
        elif spec.get('bubbleChart'):
            chart_type = 'BUBBLE_CHART'
        elif spec.get('candlestickChart'):
            chart_type = 'CANDLESTICK_CHART'
        elif spec.get('orgChart'):
            chart_type = 'ORG_CHART'
        elif spec.get('histogramChart'):
            chart_type = 'HISTOGRAM_CHART'
        elif spec.get('waterfallChart'):
            chart_type = 'WATERFALL_CHART'
        elif spec.get('treemapChart'):
            chart_type = 'TREEMAP_CHART'
        
        chart_types.append(chart_type)
        
        # Get chart title
        title = spec.get('title', '')
        chart_titles.append(title)
        
        # Get chart data ranges - handle different chart types
        ranges = []
        
        # Basic chart ranges
        if spec.get('basicChart'):
            basic_chart = spec['basicChart']
            domains = basic_chart.get('domains', [])
            series = basic_chart.get('series', [])
            
            for domain in domains:
                domain_data = domain.get('domain', {})
                source_range = domain_data.get('sourceRange', {})
                a1_range = source_range.get('sources', [{}])[0].get('a1Range', '')
                if a1_range:
                    ranges.append(a1_range)
            
            for s in series:
                series_data = s.get('series', {})
                source_range = series_data.get('sourceRange', {})
                a1_range = source_range.get('sources', [{}])[0].get('a1Range', '')
                if a1_range:
                    ranges.append(a1_range)
        
        # Pie chart ranges
        elif spec.get('pieChart'):
            pie_chart = spec['pieChart']
            domain = pie_chart.get('domain', {})
            series = pie_chart.get('series', {})
            
            domain_source = domain.get('sourceRange', {})
            series_source = series.get('sourceRange', {})
            
            domain_range = domain_source.get('sources', [{}])[0].get('a1Range', '')
            series_range = series_source.get('sources', [{}])[0].get('a1Range', '')
            
            if domain_range:
                ranges.append(domain_range)
            if series_range:
                ranges.append(series_range)
        
        # Other chart types can be added here as needed
        
        chart_ranges.append(ranges)
    
    return {
        "total_charts": total_charts,
        "chart_ids": chart_ids,
        "chart_types": chart_types,
        "chart_titles": chart_titles,
        "chart_ranges": chart_ranges
    }


def process_tables(tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process tables data for a sheet.
    
    Args:
        tables: List of tables from API
    
    Returns:
        Processed tables data
    """
    total_tables = len(tables)
    table_ids = []
    table_names = []
    table_ranges = []
    table_column_counts = []
    table_row_counts = []
    
    for table in tables:
        table_id = table.get('tableId')
        table_ids.append(table_id)
        
        # Get actual table name from the API
        name = table.get('name', f"Table{table_id}" if table_id else "Unknown")
        table_names.append(name)
        
        # Get table range
        range_info = table.get('range', {})
        table_range = range_info.get('a1Range', '')
        table_ranges.append(table_range)
        
        # Get table dimensions
        column_count = len(table.get('columnProperties', []))
        row_count = len(table.get('rowsProperties', [])) if table.get('rowsProperties') else 0
        table_column_counts.append(column_count)
        table_row_counts.append(row_count)
    
    return {
        "total_tables": total_tables,
        "table_ids": table_ids,
        "table_names": table_names,
        "table_ranges": table_ranges,
        "table_column_counts": table_column_counts,
        "table_row_counts": table_row_counts
    }


def process_slicers(slicers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process slicers data for a sheet.
    
    Args:
        slicers: List of slicers from API
    
    Returns:
        Processed slicers data
    """
    total_slicers = len(slicers)
    slicer_ids = []
    slicer_titles = []
    
    for slicer in slicers:
        slicer_id = slicer.get('slicerId')
        slicer_ids.append(slicer_id)
        
        spec = slicer.get('spec', {})
        title = spec.get('title', '')
        slicer_titles.append(title)
    
    return {
        "total_slicers": total_slicers,
        "slicer_ids": slicer_ids,
        "slicer_titles": slicer_titles
    }


def process_drawings(drawings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process drawings data for a sheet.
    
    Args:
        drawings: List of drawings from API
    
    Returns:
        Processed drawings data
    """
    total_drawings = len(drawings)
    drawing_ids = []
    
    for drawing in drawings:
        drawing_id = drawing.get('drawingId')
        drawing_ids.append(drawing_id)
    
    return {
        "total_drawings": total_drawings,
        "drawing_ids": drawing_ids
    }


def process_developer_metadata(developer_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process developer metadata for a sheet.
    
    Args:
        developer_metadata: List of developer metadata from API
    
    Returns:
        Processed developer metadata
    """
    total_metadata = len(developer_metadata)
    metadata_ids = []
    metadata_keys = []
    metadata_values = []
    
    for metadata in developer_metadata:
        metadata_id = metadata.get('metadataId')
        metadata_ids.append(metadata_id)
        
        value = metadata.get('value', '')
        metadata_values.append(value)
        
        # Get key if available
        key = metadata.get('key', '')
        metadata_keys.append(key)
    
    return {
        "total_metadata": total_metadata,
        "metadata_ids": metadata_ids,
        "metadata_keys": metadata_keys,
        "metadata_values": metadata_values
    }


def get_sheet_metadata_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str
) -> str:
    """
    Handler for getting comprehensive metadata for a specific sheet.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the specific sheet to get metadata for (required)
    
    Returns:
        Compact JSON string containing detailed sheet metadata
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    try:
        # Get detailed metadata for specific sheet
        metadata = get_detailed_sheet_metadata(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name
        )
        
        response = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "metadata": metadata,
            "message": f"Successfully retrieved detailed metadata for sheet '{sheet_name}' in '{spreadsheet_name}'"
        }
        
        # Return compact JSON string (no newlines, no spaces)
        return compact_json_response(response)
            
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            return compact_json_response({
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'"
            })
        elif "api error" in error_message.lower():
            return compact_json_response({
                "success": False,
                "message": f"Google Sheets API error: {error_message}"
            })
        else:
            return compact_json_response({
                "success": False,
                "message": f"Error getting sheet metadata: {error_message}"
            })
