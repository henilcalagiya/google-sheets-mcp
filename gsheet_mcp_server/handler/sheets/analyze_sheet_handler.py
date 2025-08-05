from typing import Dict, Any, List, Optional
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response


def analyze_sheet_comprehensive(
    sheets_service,
    spreadsheet_id: str,
    sheet_name: str
) -> Dict[str, Any]:
    """
    Comprehensive analysis of a sheet including all major elements.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet to analyze
    
    Returns:
        Dictionary with comprehensive sheet analysis
    """
    try:
        # Get comprehensive spreadsheet data with verified working fields
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.charts,sheets.tables,sheets.slicers,sheets.developerMetadata,sheets.drawings"
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
        
        return process_comprehensive_sheet_analysis(target_sheet)
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Google Sheets API error: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error analyzing sheet: {str(error)}")


def process_comprehensive_sheet_analysis(sheet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process comprehensive analysis for a single sheet.
    
    Args:
        sheet: Raw sheet data from API
    
    Returns:
        Processed comprehensive sheet analysis
    """
    props = sheet.get('properties', {})
    
    analysis = {
        "sheet_info": {
            "title": props.get('title'),
            "index": props.get('index'),
            "hidden": props.get('hidden', False),
            "tab_color": props.get('tabColor', {}),
            "right_to_left": props.get('rightToLeft', False),
            "sheet_type": props.get('sheetType', 'GRID')
        },
        "grid_properties": process_grid_properties(props.get('gridProperties', {})),
        "tables": analyze_tables(sheet.get('tables', [])),
        "charts": analyze_charts(sheet.get('charts', [])),
        "slicers": analyze_slicers(sheet.get('slicers', [])),
        "drawings": analyze_drawings(sheet.get('drawings', [])),
        "developer_metadata": analyze_developer_metadata(sheet.get('developerMetadata', []))
    }
    
    # Add fields that might not be available in the API response
    # These will be empty/default values if not present
    analysis["data_validation"] = {
        "total_validations": 0,
        "validations": [],
        "note": "Data validation information not available in current API response"
    }
    
    analysis["conditional_formatting"] = {
        "total_conditional_formats": 0,
        "conditional_formats": [],
        "note": "Conditional formatting information not available in current API response"
    }
    
    analysis["filters"] = {
        "has_filter": False,
        "note": "Filter information not available in current API response"
    }
    
    analysis["protected_ranges"] = {
        "total_protected_ranges": 0,
        "protected_ranges": [],
        "note": "Protected ranges information not available in current API response"
    }
    
    analysis["named_ranges"] = {
        "total_named_ranges": 0,
        "named_ranges": [],
        "note": "Named ranges information not available in current API response"
    }
    
    # Calculate summary statistics
    analysis["summary"] = calculate_sheet_summary(analysis)
    
    return analysis


def process_grid_properties(grid_props: Dict[str, Any]) -> Dict[str, Any]:
    """Process grid properties for a sheet."""
    return {
        "row_count": grid_props.get('rowCount', 0),
        "column_count": grid_props.get('columnCount', 0),
        "frozen_row_count": grid_props.get('frozenRowCount', 0),
        "frozen_column_count": grid_props.get('frozenColumnCount', 0),
        "hide_gridlines": grid_props.get('hideGridlines', False),
        "row_group_control_after": grid_props.get('rowGroupControlAfter', False),
        "column_group_control_after": grid_props.get('columnGroupControlAfter', False)
    }


def analyze_tables(tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze tables in the sheet."""
    total_tables = len(tables)
    table_summaries = []
    
    for table in tables:
        table_id = table.get('tableId')
        # Try different possible name fields for table names
        name = table.get('displayName') or table.get('name') or f"Table{table_id}" if table_id else "Unknown"
        
        # Get table range
        range_info = table.get('range', {})
        table_range = range_info.get('a1Range', '')
        
        # Calculate table dimensions from range if available
        start_row = range_info.get('startRowIndex', 0)
        end_row = range_info.get('endRowIndex', 0)
        start_col = range_info.get('startColumnIndex', 0)
        end_col = range_info.get('endColumnIndex', 0)
        
        # Use range-based dimensions if available, otherwise fall back to properties
        if end_row > start_row and end_col > start_col:
            row_count = end_row - start_row
            column_count = end_col - start_col
        else:
            column_count = len(table.get('columnProperties', []))
            row_count = len(table.get('rowsProperties', [])) if table.get('rowsProperties') else 0
        
        # Get column information
        columns = []
        for col_prop in table.get('columnProperties', []):
            col_name = col_prop.get('columnName', '')
            col_type = col_prop.get('columnType', 'TEXT')
            
            # Check for data validation rules
            data_validation = col_prop.get('dataValidationRule', {})
            if data_validation:
                validation_condition = data_validation.get('condition', {})
                if validation_condition.get('type') == 'ONE_OF_LIST':
                    col_type = 'DROPDOWN'
            
            columns.append({
                "name": col_name,
                "type": col_type
            })
        
        table_summaries.append({
            "name": name,
            "range": table_range,
            "column_count": column_count,
            "row_count": row_count,
            "columns": columns
        })
    
    return {
        "total_tables": total_tables,
        "tables": table_summaries
    }


def analyze_charts(charts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze charts in the sheet."""
    total_charts = len(charts)
    chart_summaries = []
    
    for chart in charts:
        chart_id = chart.get('chartId')
        spec = chart.get('spec', {})
        
        # Determine chart type
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
        
        # Get chart title
        title = spec.get('title', '')
        
        # Get chart position
        position = chart.get('position', {})
        chart_position = {
            "anchor_cell": position.get('anchorCell', {}).get('a1Address', ''),
            "offset_x": position.get('offsetX', 0),
            "offset_y": position.get('offsetY', 0)
        }
        
        chart_summaries.append({
            "chart_id": chart_id,
            "type": chart_type,
            "title": title,
            "position": chart_position
        })
    
    return {
        "total_charts": total_charts,
        "charts": chart_summaries
    }


def analyze_slicers(slicers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze slicers in the sheet."""
    total_slicers = len(slicers)
    slicer_summaries = []
    
    for slicer in slicers:
        slicer_id = slicer.get('slicerId')
        spec = slicer.get('spec', {})
        
        title = spec.get('title', '')
        column_index = spec.get('columnIndex', 0)
        
        slicer_summaries.append({
            "slicer_id": slicer_id,
            "title": title,
            "column_index": column_index
        })
    
    return {
        "total_slicers": total_slicers,
        "slicers": slicer_summaries
    }


def analyze_drawings(drawings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze drawings in the sheet."""
    total_drawings = len(drawings)
    drawing_summaries = []
    
    for drawing in drawings:
        drawing_id = drawing.get('drawingId')
        drawing_summaries.append({
            "drawing_id": drawing_id
        })
    
    return {
        "total_drawings": total_drawings,
        "drawings": drawing_summaries
    }


def analyze_data_validation(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze data validation rules in the sheet."""
    total_validations = len(validations)
    validation_summaries = []
    
    for validation in validations:
        rule = validation.get('condition', {})
        validation_type = rule.get('type', 'UNKNOWN')
        
        validation_range = validation.get('range', {}).get('a1Range', '')
        
        validation_summary = {
            "type": validation_type,
            "range": validation_range,
            "strict": validation.get('strict', False),
            "show_custom_ui": validation.get('showCustomUi', False)
        }
        
        if validation_type == 'ONE_OF_LIST':
            values = rule.get('values', [])
            validation_summary["dropdown_options"] = [v.get('userEnteredValue', '') for v in values]
        
        validation_summaries.append(validation_summary)
    
    return {
        "total_validations": total_validations,
        "validations": validation_summaries
    }


def analyze_conditional_formatting(conditional_formats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze conditional formatting rules in the sheet."""
    total_formats = len(conditional_formats)
    format_summaries = []
    
    for format_rule in conditional_formats:
        ranges = format_rule.get('ranges', [])
        rule = format_rule.get('booleanRule', {})
        
        condition = rule.get('condition', {})
        format_type = condition.get('type', 'UNKNOWN')
        
        format_summary = {
            "ranges": [r.get('a1Range', '') for r in ranges],
            "condition_type": format_type,
            "format_applied": bool(rule.get('format'))
        }
        
        format_summaries.append(format_summary)
    
    return {
        "total_conditional_formats": total_formats,
        "conditional_formats": format_summaries
    }


def analyze_filters(basic_filter: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze filters in the sheet."""
    if not basic_filter:
        return {"has_filter": False}
    
    range_info = basic_filter.get('range', {})
    filter_range = range_info.get('a1Range', '')
    
    filter_criteria = basic_filter.get('criteria', {})
    total_criteria = len(filter_criteria)
    
    return {
        "has_filter": True,
        "filter_range": filter_range,
        "total_criteria": total_criteria,
        "criteria": list(filter_criteria.keys())
    }


def analyze_protected_ranges(protected_ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze protected ranges in the sheet."""
    total_protected = len(protected_ranges)
    protected_summaries = []
    
    for protected in protected_ranges:
        protected_id = protected.get('protectedRangeId')
        range_info = protected.get('range', {})
        protected_range = range_info.get('a1Range', '')
        
        protected_summary = {
            "protected_range_id": protected_id,
            "range": protected_range,
            "description": protected.get('description', ''),
            "warning_only": protected.get('warningOnly', False)
        }
        
        protected_summaries.append(protected_summary)
    
    return {
        "total_protected_ranges": total_protected,
        "protected_ranges": protected_summaries
    }


def analyze_named_ranges(named_ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze named ranges in the sheet."""
    total_named_ranges = len(named_ranges)
    named_range_summaries = []
    
    for named_range in named_ranges:
        name = named_range.get('name', '')
        range_info = named_range.get('range', {})
        named_range_address = range_info.get('a1Range', '')
        
        named_range_summaries.append({
            "name": name,
            "range": named_range_address
        })
    
    return {
        "total_named_ranges": total_named_ranges,
        "named_ranges": named_range_summaries
    }


def analyze_developer_metadata(developer_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze developer metadata in the sheet."""
    total_metadata = len(developer_metadata)
    metadata_summaries = []
    
    for metadata in developer_metadata:
        metadata_id = metadata.get('metadataId')
        value = metadata.get('value', '')
        key = metadata.get('key', '')
        
        metadata_summaries.append({
            "metadata_id": metadata_id,
            "key": key,
            "value": value
        })
    
    return {
        "total_developer_metadata": total_metadata,
        "developer_metadata": metadata_summaries
    }


def calculate_sheet_summary(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate summary statistics for the sheet."""
    grid_props = analysis.get('grid_properties', {})
    tables = analysis.get('tables', {})
    charts = analysis.get('charts', {})
    slicers = analysis.get('slicers', {})
    drawings = analysis.get('drawings', {})
    validations = analysis.get('data_validation', {})
    conditional_formats = analysis.get('conditional_formatting', {})
    filters = analysis.get('filters', {})
    protected_ranges = analysis.get('protected_ranges', {})
    named_ranges = analysis.get('named_ranges', {})
    developer_metadata = analysis.get('developer_metadata', {})
    
    summary = {
        "total_rows": grid_props.get('row_count', 0),
        "total_columns": grid_props.get('column_count', 0),
        "total_cells": grid_props.get('row_count', 0) * grid_props.get('column_count', 0),
        "has_frozen_panes": grid_props.get('frozen_row_count', 0) > 0 or grid_props.get('frozen_column_count', 0) > 0,
        "total_tables": tables.get('total_tables', 0),
        "total_charts": charts.get('total_charts', 0),
        "total_slicers": slicers.get('total_slicers', 0),
        "total_drawings": drawings.get('total_drawings', 0),
        "total_validations": validations.get('total_validations', 0),
        "total_conditional_formats": conditional_formats.get('total_conditional_formats', 0),
        "has_filter": filters.get('has_filter', False),
        "total_protected_ranges": protected_ranges.get('total_protected_ranges', 0),
        "total_named_ranges": named_ranges.get('total_named_ranges', 0),
        "total_developer_metadata": developer_metadata.get('total_developer_metadata', 0)
    }
    
    # Calculate complexity score
    complexity_score = (
        summary["total_tables"] * 2 +
        summary["total_charts"] * 1.5 +
        summary["total_slicers"] * 1 +
        summary["total_validations"] * 0.5 +
        summary["total_conditional_formats"] * 0.5 +
        (1 if summary["has_filter"] else 0) * 1 +
        summary["total_protected_ranges"] * 0.5
    )
    
    summary["complexity_score"] = round(complexity_score, 1)
    
    # Determine sheet type
    if summary["total_tables"] > 0:
        summary["sheet_type"] = "DATA_TABLE"
    elif summary["total_charts"] > 0:
        summary["sheet_type"] = "CHART_DASHBOARD"
    elif summary["has_filter"] or summary["total_conditional_formats"] > 0:
        summary["sheet_type"] = "ANALYSIS_SHEET"
    else:
        summary["sheet_type"] = "GENERAL_SHEET"
    
    return summary


def analyze_sheet_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str
) -> str:
    """
    Handler for comprehensive sheet analysis.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the specific sheet to analyze
    
    Returns:
        Compact JSON string containing comprehensive sheet analysis
    """
    try:
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        if not spreadsheet_id:
            return compact_json_response({
                "success": False,
                "message": f"Spreadsheet '{spreadsheet_name}' not found."
            })
        
        # Get comprehensive analysis for specific sheet
        analysis = analyze_sheet_comprehensive(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name
        )
        
        response = {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "analysis": analysis,
            "message": f"Successfully analyzed sheet '{sheet_name}' in '{spreadsheet_name}'"
        }
        
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
                "message": f"Error analyzing sheet: {error_message}"
            }) 