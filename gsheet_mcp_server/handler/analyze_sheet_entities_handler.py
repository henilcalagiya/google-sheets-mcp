from typing import Dict, Any, List, Optional
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.handler.read_sheet_data_handler import get_sheet_metadata, read_multiple_ranges


class AnalyzeSheetEntitiesRequest(BaseModel):
    """Request model for analyzing sheet entities."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet to analyze")


class AnalyzeSheetEntitiesResponse(BaseModel):
    """Response model for analyzing sheet entities."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    entities: Dict[str, Any]
    message: str


def analyze_sheet_entities(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str
) -> Dict[str, Any]:
    """
    Analyze a sheet for core data entities: tables, charts, and scattered cells.
    
    This function provides focused analysis of:
    - Data tables and their structure
    - Charts and their configurations
    - Scattered cells (independent cells not part of tables)
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to analyze
    
    Returns:
        Dict containing detailed analysis of core entities in the sheet
        
    Raises:
        RuntimeError: If sheet not found or other errors occur
    """
    try:
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        
        # Get sheet metadata
        metadata = get_sheet_metadata(sheets_service, spreadsheet_id, sheet_name)
        if 'sheet' not in metadata:
            raise RuntimeError(f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'")
        
        sheet_info = metadata['sheet']
        sheet_id = sheet_info.get('sheet_id')
        
        # Analyze different entities
        entities_analysis = {
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "sheet_id": sheet_id,
            "entities": {
                "data_tables": [],
                "scattered_cells": [],
                "charts": [],
                "summary": {}
            }
        }
        
        # 1. Analyze Data Tables
        data_tables = _analyze_data_tables(
            sheets_service, spreadsheet_id, sheet_id, sheet_name
        )
        entities_analysis["entities"]["data_tables"] = data_tables
        
        # 2. Analyze Scattered Cells (independent cells)
        scattered_cells = _analyze_scattered_cells(
            sheets_service, spreadsheet_id, sheet_id, sheet_name, data_tables
        )
        entities_analysis["entities"]["scattered_cells"] = scattered_cells
        
        # 3. Analyze Charts
        charts = _analyze_charts(sheets_service, spreadsheet_id, sheet_id)
        entities_analysis["entities"]["charts"] = charts
        
        # 4. Create Summary
        summary = _create_entities_summary(entities_analysis["entities"])
        entities_analysis["entities"]["summary"] = summary
        
        # Add message
        entities_analysis["message"] = (
            f"Sheet '{sheet_name}' entities analysis complete. "
            f"Found {len(data_tables)} data tables, {len(scattered_cells)} scattered cells, "
            f"{len(charts)} charts."
        )
        
        return entities_analysis
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error analyzing sheet entities: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error analyzing sheet entities: {error}")


def _analyze_data_tables(sheets_service, spreadsheet_id: str, sheet_id: int, sheet_name: str) -> List[Dict[str, Any]]:
    """Analyze data tables in the sheet."""
    tables = []
    
    # 1. First, detect native Google Sheets tables (created with AddTableRequest)
    native_tables = _detect_native_tables(sheets_service, spreadsheet_id, sheet_name)
    tables.extend(native_tables)
    
    # 2. Then detect data tables based on patterns
    pattern_tables = _detect_pattern_tables(sheets_service, spreadsheet_id, sheet_id, sheet_name)
    tables.extend(pattern_tables)
    
    return tables


def _detect_native_tables(sheets_service, spreadsheet_id: str, sheet_name: str) -> List[Dict[str, Any]]:
    """Detect native Google Sheets tables created with AddTableRequest."""
    try:
        # Get spreadsheet to find native tables
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties,sheets.tables"
        ).execute()
        
        native_tables = []
        
        # Search for tables in the specified sheet
        for sheet in result.get("sheets", []):
            props = sheet.get("properties", {})
            if props.get("title") == sheet_name:
                tables = sheet.get("tables", [])
                
                for table in tables:
                    table_range = table.get("range", {})
                    native_tables.append({
                        "table_name": table.get("name", "Unknown"),
                        "table_type": "native_google_table",
                        "start_row": table_range.get("startRowIndex", 0) + 1,
                        "end_row": table_range.get("endRowIndex", 0),
                        "start_column": table_range.get("startColumnIndex", 0) + 1,
                        "end_column": table_range.get("endColumnIndex", 0),
                        "row_count": table_range.get("endRowIndex", 0) - table_range.get("startRowIndex", 0),
                        "column_count": table_range.get("endColumnIndex", 0) - table_range.get("startColumnIndex", 0),
                        "has_headers": True,  # Native tables typically have headers
                        "column_properties": table.get("columnProperties", []),
                        "rows_properties": table.get("rowsProperties", [])
                    })
                break
        
        return native_tables
        
    except Exception as e:
        return []


def _detect_pattern_tables(sheets_service, spreadsheet_id: str, sheet_id: int, sheet_name: str) -> List[Dict[str, Any]]:
    """Detect data tables based on data patterns."""
    try:
        # Read sheet data to identify tables
        ranges = [f'{sheet_name}!A:ZZ']
        data_result = read_multiple_ranges(
            drive_service=None,  # Not needed for this call
            sheets_service=sheets_service,
            spreadsheet_name="",  # Not needed for this call
            ranges=ranges,
            value_render_option="UNFORMATTED_VALUE"
        )
        
        if not data_result.get('ranges'):
            return []
        
        values = data_result['ranges'][0]['values']
        tables = []
        
        # Simple table detection based on data patterns
        if values:
            # Find table boundaries
            table_boundaries = _find_table_boundaries(values)
            
            for i, (start_row, end_row, start_col, end_col) in enumerate(table_boundaries):
                table_data = values[start_row:end_row]
                headers = table_data[0] if table_data else []
                
                tables.append({
                    "table_name": f"Pattern Table {i + 1}",
                    "table_type": "pattern_detected_table",
                    "start_row": start_row + 1,
                    "end_row": end_row,
                    "start_column": start_col + 1,
                    "end_column": end_col,
                    "headers": headers,
                    "row_count": len(table_data),
                    "column_count": len(headers),
                    "has_headers": bool(headers and any(headers))
                })
        
        return tables
        
    except Exception as e:
        return []


def _find_table_boundaries(values: List[List[Any]]) -> List[tuple]:
    """Find boundaries of data tables in the sheet."""
    if not values:
        return []
    
    boundaries = []
    current_start = 0
    
    for i, row in enumerate(values):
        has_data = any(cell and str(cell).strip() for cell in row)
        
        if has_data and current_start == -1:
            current_start = i
        elif not has_data and current_start != -1:
            # End of table
            if i - current_start > 1:  # At least 2 rows
                boundaries.append((current_start, i, 0, len(row)))
            current_start = -1
    
    # Handle table at the end
    if current_start != -1 and len(values) - current_start > 1:
        boundaries.append((current_start, len(values), 0, len(values[0]) if values else 0))
    
    return boundaries


def _analyze_scattered_cells(sheets_service, spreadsheet_id: str, sheet_id: int, sheet_name: str, data_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze scattered/independent cells that are not part of structured tables."""
    try:
        # Read sheet data
        ranges = [f'{sheet_name}!A:ZZ']
        data_result = read_multiple_ranges(
            drive_service=None,
            sheets_service=sheets_service,
            spreadsheet_name="",
            ranges=ranges,
            value_render_option="UNFORMATTED_VALUE"
        )
        
        if not data_result.get('ranges'):
            return []
        
        values = data_result['ranges'][0]['values']
        scattered_cells = []
        
        # Create a set of cells that are part of tables (both native and pattern-detected)
        table_cells = set()
        for table in data_tables:
            start_row = table.get('start_row', 1) - 1  # Convert to 0-based
            end_row = table.get('end_row', 1)
            start_col = table.get('start_column', 1) - 1  # Convert to 0-based
            end_col = table.get('end_column', 1)
            
            for row_idx in range(start_row, end_row):
                for col_idx in range(start_col, end_col):
                    table_cells.add((row_idx, col_idx))
        
        # Find scattered cells (cells with data that are not in tables)
        for row_idx, row in enumerate(values):
            for col_idx, cell_value in enumerate(row):
                if cell_value and str(cell_value).strip():  # Non-empty cell
                    if (row_idx, col_idx) not in table_cells:
                        # This is a scattered cell
                        scattered_cells.append({
                            "cell_reference": f"{chr(65 + col_idx)}{row_idx + 1}",  # A1 notation
                            "row": row_idx + 1,
                            "column": col_idx + 1,
                            "value": cell_value,
                            "value_type": _get_value_type(cell_value),
                            "category": _categorize_scattered_cell(cell_value, row_idx, col_idx)
                        })
        
        return scattered_cells
        
    except Exception as e:
        return []


def _get_value_type(value: Any) -> str:
    """Determine the type of a cell value."""
    if isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, str):
        # Check if it's a date
        try:
            import datetime
            datetime.datetime.strptime(value, "%Y-%m-%d")
            return "date"
        except:
            pass
        
        # Check if it's a formula
        if value.startswith('='):
            return "formula"
        
        return "text"
    else:
        return "unknown"


def _categorize_scattered_cell(value: Any, row_idx: int, col_idx: int) -> str:
    """Categorize scattered cells based on their content and position."""
    value_str = str(value).lower()
    
    # Check for common patterns
    if value_str in ['total', 'sum', 'average', 'count', 'max', 'min']:
        return "calculation_label"
    elif value_str in ['title', 'header', 'name', 'date', 'amount', 'quantity']:
        return "field_label"
    elif value_str.startswith('note') or value_str.startswith('comment'):
        return "note"
    elif row_idx == 0 or col_idx == 0:  # First row or column
        return "header_or_label"
    elif _get_value_type(value) == "formula":
        return "calculation"
    elif _get_value_type(value) == "number":
        return "standalone_value"
    else:
        return "general_data"


def _analyze_charts(sheets_service, spreadsheet_id: str, sheet_id: int) -> List[Dict[str, Any]]:
    """Analyze charts in the sheet."""
    try:
        # Get charts for this sheet
        charts_result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets(charts)"
        ).execute()
        
        charts = []
        for sheet in charts_result.get('sheets', []):
            if sheet.get('charts'):
                for chart in sheet['charts']:
                    charts.append({
                        "chart_id": chart.get('chartId'),
                        "position": chart.get('position', {}),
                        "spec": chart.get('spec', {}),
                        "title": chart.get('spec', {}).get('title', ''),
                        "chart_type": chart.get('spec', {}).get('basicChart', {}).get('chartType', '')
                    })
        
        return charts
        
    except Exception as e:
        return []


def _create_entities_summary(entities: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of all entities found."""
    summary = {
        "total_entities": 0,
        "entity_types": {},
        "complexity_score": 0
    }
    
    for entity_type, entity_list in entities.items():
        if entity_type != "summary":
            count = len(entity_list)
            summary["entity_types"][entity_type] = count
            summary["total_entities"] += count
    
    # Calculate complexity score (1-10)
    complexity_factors = {
        "data_tables": 2,
        "scattered_cells": 1,
        "charts": 1
    }
    
    complexity_score = 0
    for entity_type, count in summary["entity_types"].items():
        complexity_score += count * complexity_factors.get(entity_type, 1)
    
    summary["complexity_score"] = min(10, complexity_score)
    
    return summary 