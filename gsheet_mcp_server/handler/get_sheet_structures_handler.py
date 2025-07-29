from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names

class SheetStructureInfo(BaseModel):
    """Information about a sheet structure."""
    structure_type: str
    name: str
    range: str
    description: str

class SheetStructuresResponse(BaseModel):
    """Response model for listing sheet structures."""
    spreadsheet_name: str
    sheet_name: str
    sheet_id: int
    structures: List[SheetStructureInfo]
    summary: Dict[str, int]
    message: str

def col_to_letter(col_num):
    """Convert column number to A1 notation letter."""
    if col_num <= 26:
        return chr(64 + col_num)
    elif col_num <= 702:  # ZZ
        return chr(64 + (col_num - 1) // 26) + chr(64 + ((col_num - 1) % 26) + 1)
    else:
        return f"A{col_num}"  # Fallback for very large column numbers

def get_sheet_structures(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str
) -> Dict[str, Any]:
    """
    Get all structures found in a Google Sheet.
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet
    
    Returns:
        Dict containing sheet structures information
    """
    
    # Validate input
    if not sheet_name:
        return {
            "success": False,
            "message": "No sheet name provided."
        }
    
    # Get spreadsheet ID
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return {
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        }
    
    # Get sheet ID from sheet name
    sheet_id_map = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
    sheet_id = sheet_id_map.get(sheet_name)
    
    if sheet_id is None:
        return {
            "success": False,
            "message": f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'."
        }
    
    try:
        # Get detailed spreadsheet information using optimal API fields
        # Using the correct fields as per Google Sheets API documentation
        try:
            spreadsheet = sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields="sheets(properties,tables,charts),namedRanges"
            ).execute()
        except Exception as api_error:
            return {
                "success": False,
                "message": f"API Error: {str(api_error)}. Please check if the spreadsheet and sheet exist."
            }
        
        structures = []
        summary = {
            "tables": 0,
            "charts": 0,
            "named_ranges": 0
        }
        
        # Find the specific sheet
        target_sheet = None
        available_sheets = []
        for sheet in spreadsheet.get("sheets", []):
            sheet_title = sheet.get("properties", {}).get("title", "Unknown")
            available_sheets.append(sheet_title)
            if sheet_title == sheet_name:
                target_sheet = sheet
                break
        
        if not target_sheet:
            return {
                "success": False,
                "message": f"Sheet '{sheet_name}' not found in spreadsheet. Available sheets: {available_sheets}"
            }
        
        # Get native tables from API (most accurate)
        native_tables = target_sheet.get("tables", [])
        for table in native_tables:
            table_props = table.get("tableProperties", {})
            table_range = table_props.get("range", {})
            
            # Convert range to A1 notation
            start_row = table_range.get("startRowIndex", 0) + 1
            end_row = table_range.get("endRowIndex", 0)
            start_col = table_range.get("startColumnIndex", 0) + 1
            end_col = table_range.get("endColumnIndex", 0)
            
            start_col_letter = col_to_letter(start_col)
            end_col_letter = col_to_letter(end_col)
            range_str = f"{start_col_letter}{start_row}:{end_col_letter}{end_row}"
            
            structures.append({
                "structure_type": "native_table",
                "name": table_props.get("displayName", f"Table_{len([s for s in structures if s['structure_type'] == 'native_table']) + 1}"),
                "range": range_str,
                "description": f"Native table with {end_row - start_row + 1} rows and {end_col - start_col + 1} columns"
            })
            summary["tables"] += 1
        
        # Note: Pivot tables are not directly accessible via API fields
        # They would need to be detected through data analysis
        # For now, we'll skip pivot table detection
        
        # Note: Filter views are not directly accessible via API fields
        # They would need to be detected through data analysis
        # For now, we'll skip filter view detection
        
        # Get charts
        charts = target_sheet.get("charts", [])
        for chart in charts:
            chart_spec = chart.get("spec", {})
            chart_name = chart_spec.get("title", f"Chart_{len([s for s in structures if s['structure_type'] == 'chart']) + 1}")
            
            # Safely extract chart position
            position_info = chart.get("position", {})
            overlay_position = position_info.get("overlayPosition", {})
            anchor_cell = overlay_position.get("anchorCell", {})
            chart_position = f"Chart at {anchor_cell.get('sheetId', 'unknown')}"
            
            structures.append({
                "structure_type": "chart",
                "name": chart_name,
                "range": chart_position,
                "description": f"{chart_spec.get('chartType', 'Unknown')} chart"
            })
            summary["charts"] += 1
        
        # Get named ranges that belong to this sheet
        named_ranges = spreadsheet.get("namedRanges", [])
        for named_range in named_ranges:
            ranges = named_range.get("ranges", [])
            for range_info in ranges:
                if range_info.get("sheetId") == sheet_id:
                    start_row = range_info.get("startRowIndex", 0) + 1
                    end_row = range_info.get("endRowIndex", 0)
                    start_col = range_info.get("startColumnIndex", 0) + 1
                    end_col = range_info.get("endColumnIndex", 0)
                    
                    # Convert to A1 notation
                    start_col_letter = col_to_letter(start_col)
                    end_col_letter = col_to_letter(end_col)
                    
                    range_str = f"{start_col_letter}{start_row}:{end_col_letter}{end_row}"
                    
                    structures.append({
                        "structure_type": "named_range",
                        "name": named_range.get("name", "Unknown"),
                        "range": range_str,
                        "description": f"Named range: {named_range.get('name', 'Unknown')}"
                    })
                    summary["named_ranges"] += 1
        
        # Get data to detect non-native structures (regular tables, scattered data)
        try:
            # Get a sample of data to detect patterns
            data_response = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:Z1000"
            ).execute()
            
            values = data_response.get("values", [])
            if values:
                # Detect regular data tables (non-native)
                regular_tables = _detect_regular_tables(values)
                for table in regular_tables:
                    structures.append({
                        "structure_type": "regular_table",
                        "name": f"DataTable_{len([s for s in structures if s['structure_type'] == 'regular_table']) + 1}",
                        "range": table["range"],
                        "description": f"Regular data table with {table['rows']} rows and {table['columns']} columns"
                    })
                    summary["tables"] += 1
                
                # Detect scattered data areas
                scattered_areas = _detect_scattered_data(values, regular_tables)
                for area in scattered_areas:
                    structures.append({
                        "structure_type": "scattered_data",
                        "name": f"ScatteredData_{len([s for s in structures if s['structure_type'] == 'scattered_data']) + 1}",
                        "range": area["range"],
                        "description": f"Scattered data area with {area['cells']} cells"
                    })
                    summary["scattered_data"] = summary.get("scattered_data", 0) + 1
                    
        except Exception as e:
            print(f"Warning: Error detecting data patterns: {e}")
        
        # Note: Protected ranges are not directly accessible via API fields
        # They would need to be detected through data analysis
        # For now, we'll skip protected range detection
        
        # Note: Developer metadata is not directly accessible via API fields
        # It would need to be detected through data analysis
        # For now, we'll skip developer metadata detection
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "sheet_id": sheet_id,
            "structures": structures,
            "summary": summary,
            "message": f"Found {len(structures)} data structures in sheet '{sheet_name}'."
        }
        
    except HttpError as error:
        return {
            "success": False,
            "message": f"Error listing data structures: {error}"
        }
    except Exception as error:
        return {
            "success": False,
            "message": f"Unexpected error: {error}"
        }

def _detect_regular_tables(values):
    """Detect regular data tables (non-native) in the sheet."""
    tables = []
    if not values:
        return tables
    
    # Simple table detection: look for contiguous data with headers
    current_table = None
    
    for row_idx, row in enumerate(values):
        if not row:
            continue
        
        # Check if this row has data
        has_data = any(cell.strip() for cell in row if cell)
        
        if has_data:
            if current_table is None:
                # Start new table
                current_table = {
                    "start_row": row_idx,
                    "end_row": row_idx,
                    "columns": len(row)
                }
            else:
                # Extend current table
                current_table["end_row"] = row_idx
                current_table["columns"] = max(current_table["columns"], len(row))
        else:
            # End current table if we have one
            if current_table and current_table["end_row"] - current_table["start_row"] >= 0:
                tables.append({
                    "range": f"A{current_table['start_row'] + 1}:{chr(65 + current_table['columns'] - 1)}{current_table['end_row'] + 1}",
                    "rows": current_table["end_row"] - current_table["start_row"] + 1,
                    "columns": current_table["columns"]
                })
                current_table = None
    
    # Add final table if exists
    if current_table and current_table["end_row"] - current_table["start_row"] >= 0:
        tables.append({
            "range": f"A{current_table['start_row'] + 1}:{chr(65 + current_table['columns'] - 1)}{current_table['end_row'] + 1}",
            "rows": current_table["end_row"] - current_table["start_row"] + 1,
            "columns": current_table["columns"]
        })
    
    return tables

def _detect_scattered_data(values, tables):
    """Detect scattered data areas (non-table areas)."""
    scattered_areas = []
    if not values:
        return scattered_areas
    
    # Get all table ranges
    table_ranges = set()
    for table in tables:
        table_ranges.add(table["range"])
    
    # Find areas that are not part of tables
    current_area = None
    
    for row_idx, row in enumerate(values):
        if not row:
            continue
        
        # Check if this row has data outside of tables
        has_scattered_data = False
        for col_idx, cell in enumerate(row):
            if cell and cell.strip():
                cell_range = f"{chr(65 + col_idx)}{row_idx + 1}"
                # Check if this cell is part of any table
                in_table = False
                for table_range in table_ranges:
                    # Simplified check - in real implementation would need proper range parsing
                    if cell_range in table_range:
                        in_table = True
                        break
                
                if not in_table:
                    has_scattered_data = True
                    break
        
        if has_scattered_data:
            if current_area is None:
                current_area = {
                    "start_row": row_idx,
                    "end_row": row_idx,
                    "cells": 0
                }
            else:
                current_area["end_row"] = row_idx
            
            # Count cells in this row
            for cell in row:
                if cell and cell.strip():
                    current_area["cells"] += 1
        else:
            # End current area if we have one
            if current_area and current_area["cells"] > 0:
                scattered_areas.append({
                    "range": f"A{current_area['start_row'] + 1}:Z{current_area['end_row'] + 1}",
                    "cells": current_area["cells"]
                })
                current_area = None
    
    # Add final area if exists
    if current_area and current_area["cells"] > 0:
        scattered_areas.append({
            "range": f"A{current_area['start_row'] + 1}:Z{current_area['end_row'] + 1}",
            "cells": current_area["cells"]
        })
    
    return scattered_areas

 