from typing import Dict, Any, List, Set, Tuple
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
    # Handle edge case where col_num is 0 or negative
    if col_num <= 0:
        return "A"  # Default to column A
    
    if col_num <= 26:
        return chr(64 + col_num)
    elif col_num <= 702:  # ZZ
        return chr(64 + (col_num - 1) // 26) + chr(64 + ((col_num - 1) % 26) + 1)
    else:
        return f"A{col_num}"  # Fallback for very large column numbers

def letter_to_col(letter):
    """Convert A1 notation letter to column number."""
    col = 0
    for char in letter.upper():
        col = col * 26 + (ord(char) - ord('A') + 1)
    return col

def parse_range(range_str: str) -> Tuple[int, int, int, int]:
    """
    Parse A1 notation range to (start_row, end_row, start_col, end_col).
    Returns 1-based indices.
    """
    if ':' not in range_str:
        # Single cell like "A1"
        col_letter = ''.join(c for c in range_str if c.isalpha())
        row_num = int(''.join(c for c in range_str if c.isdigit()))
        col_num = letter_to_col(col_letter)
        return row_num, row_num, col_num, col_num
    
    # Range like "A1:C10"
    start, end = range_str.split(':')
    
    # Parse start
    start_col_letter = ''.join(c for c in start if c.isalpha())
    start_row = int(''.join(c for c in start if c.isdigit()))
    start_col = letter_to_col(start_col_letter)
    
    # Parse end
    end_col_letter = ''.join(c for c in end if c.isalpha())
    end_row = int(''.join(c for c in end if c.isdigit()))
    end_col = letter_to_col(end_col_letter)
    
    return start_row, end_row, start_col, end_col

def is_cell_in_range(cell: str, range_str: str) -> bool:
    """
    Check if a cell (e.g., "B5") is within a range (e.g., "A1:C10").
    """
    try:
        cell_col_letter = ''.join(c for c in cell if c.isalpha())
        cell_row = int(''.join(c for c in cell if c.isdigit()))
        cell_col = letter_to_col(cell_col_letter)
        
        start_row, end_row, start_col, end_col = parse_range(range_str)
        
        return (start_row <= cell_row <= end_row and 
                start_col <= cell_col <= end_col)
    except:
        return False

def ranges_overlap(range1: str, range2: str) -> bool:
    """
    Check if two ranges overlap (not just exact match).
    """
    try:
        start_row1, end_row1, start_col1, end_col1 = parse_range(range1)
        start_row2, end_row2, start_col2, end_col2 = parse_range(range2)
        
        # Check for overlap: ranges overlap if they intersect in both dimensions
        rows_overlap = not (end_row1 < start_row2 or end_row2 < start_row1)
        cols_overlap = not (end_col1 < start_col2 or end_col2 < start_col1)
        
        return rows_overlap and cols_overlap
    except:
        return False

def get_all_table_ranges(native_tables: List[Dict], regular_tables: List[Dict]) -> Set[str]:
    """
    Collect all table ranges (native and regular) to avoid overlaps.
    """
    all_ranges = set()
    
    # Add native table ranges
    for table in native_tables:
        table_props = table.get("tableProperties", {})
        table_range = table_props.get("range", {})
        
        # Convert to A1 notation with validation
        start_row = max(1, table_range.get("startRowIndex", 0) + 1)
        start_col = max(1, table_range.get("startColumnIndex", 0) + 1)
        
        # Handle end indices properly for table ranges
        raw_end_row = table_range.get("endRowIndex", 0)
        raw_end_col = table_range.get("endColumnIndex", 0)
        
        if raw_end_row <= 0:
            end_row = start_row + 3  # Default to 4 rows
        else:
            end_row = raw_end_row
        
        if raw_end_col <= 0:
            end_col = start_col + 4  # Default to 5 columns
        else:
            end_col = raw_end_col
        
        start_col_letter = col_to_letter(start_col)
        end_col_letter = col_to_letter(end_col)
        range_str = f"{start_col_letter}{start_row}:{end_col_letter}{end_row}"
        all_ranges.add(range_str)
    
    # Add regular table ranges
    for table in regular_tables:
        all_ranges.add(table["range"])
    
    return all_ranges

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
            
            # Convert range to A1 notation with validation
            start_row = max(1, table_range.get("startRowIndex", 0) + 1)
            start_col = max(1, table_range.get("startColumnIndex", 0) + 1)
            
            # Handle end indices properly - if they're 0 or missing, we need to infer them
            raw_end_row = table_range.get("endRowIndex", 0)
            raw_end_col = table_range.get("endColumnIndex", 0)
            
            # If end indices are 0 or missing, we need to handle this differently
            if raw_end_row <= 0:
                # For now, use a reasonable default - in a real implementation,
                # we would try to infer this from the actual data
                end_row = start_row + 3  # Default to 4 rows if we can't determine
            else:
                end_row = raw_end_row
            
            if raw_end_col <= 0:
                # For now, use a reasonable default - in a real implementation,
                # we would try to infer this from the actual data
                end_col = start_col + 4  # Default to 5 columns if we can't determine
            else:
                end_col = raw_end_col
            

            
            start_col_letter = col_to_letter(start_col)
            end_col_letter = col_to_letter(end_col)
            range_str = f"{start_col_letter}{start_row}:{end_col_letter}{end_row}"
            
            # Get the actual table name, fallback to auto-generated if empty
            # Try different possible field names for table name
            table_name = table.get("displayName", "")  # Try table root first
            if not table_name or table_name.strip() == "":
                table_name = table_props.get("displayName", "")  # Try tableProperties
            if not table_name or table_name.strip() == "":
                table_name = table.get("name", "")  # Try table root
            if not table_name or table_name.strip() == "":
                table_name = table_props.get("name", "")  # Try tableProperties
            if not table_name or table_name.strip() == "":
                table_name = table.get("title", "")  # Try table root
            if not table_name or table_name.strip() == "":
                table_name = table_props.get("title", "")  # Try tableProperties
            if not table_name or table_name.strip() == "":
                table_name = table.get("id", "")  # Try table root
            if not table_name or table_name.strip() == "":
                table_name = table_props.get("id", "")  # Try tableProperties
            
            if not table_name or table_name.strip() == "":
                table_name = f"Table_{len([s for s in structures if s['structure_type'] == 'native_table']) + 1}"
            
            structures.append({
                "structure_type": "native_table",
                "name": table_name,
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
            
            # Try different possible field names for chart name
            chart_name = chart.get("title", "")  # Try chart root first
            if not chart_name or chart_name.strip() == "":
                chart_name = chart_spec.get("title", "")  # Try chart spec
            if not chart_name or chart_name.strip() == "":
                chart_name = chart.get("name", "")  # Try chart root
            if not chart_name or chart_name.strip() == "":
                chart_name = chart_spec.get("name", "")  # Try chart spec
            if not chart_name or chart_name.strip() == "":
                chart_name = chart.get("displayName", "")  # Try chart root
            if not chart_name or chart_name.strip() == "":
                chart_name = chart_spec.get("displayName", "")  # Try chart spec
            if not chart_name or chart_name.strip() == "":
                chart_name = chart.get("id", "")  # Try chart root
            if not chart_name or chart_name.strip() == "":
                chart_name = chart_spec.get("id", "")  # Try chart spec
            
            if not chart_name or chart_name.strip() == "":
                chart_name = f"Chart_{len([s for s in structures if s['structure_type'] == 'chart']) + 1}"
            
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
                    start_row = max(1, range_info.get("startRowIndex", 0) + 1)
                    start_col = max(1, range_info.get("startColumnIndex", 0) + 1)
                    
                    # Handle end indices properly for named ranges
                    raw_end_row = range_info.get("endRowIndex", 0)
                    raw_end_col = range_info.get("endColumnIndex", 0)
                    
                    if raw_end_row <= 0:
                        end_row = start_row + 3  # Default to 4 rows
                    else:
                        end_row = raw_end_row
                    
                    if raw_end_col <= 0:
                        end_col = start_col + 4  # Default to 5 columns
                    else:
                        end_col = raw_end_col
                    
                    # Convert to A1 notation
                    start_col_letter = col_to_letter(start_col)
                    end_col_letter = col_to_letter(end_col)
                    
                    range_str = f"{start_col_letter}{start_row}:{end_col_letter}{end_row}"
                    
                    # Try different possible field names for named range name
                    range_name = named_range.get("name", "")
                    if not range_name or range_name.strip() == "":
                        range_name = named_range.get("displayName", "")
                    if not range_name or range_name.strip() == "":
                        range_name = named_range.get("title", "")
                    if not range_name or range_name.strip() == "":
                        range_name = named_range.get("id", "")
                    
                    if not range_name or range_name.strip() == "":
                        range_name = "Unknown"
                    
                    structures.append({
                        "structure_type": "named_range",
                        "name": range_name,
                        "range": range_str,
                        "description": f"Named range: {range_name}"
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
                
                # Get all table ranges (native + regular) to avoid overlaps
                all_table_ranges = get_all_table_ranges(native_tables, regular_tables)
                
                # Filter out regular tables that overlap with native tables
                non_overlapping_regular_tables = []
                for table in regular_tables:
                    # Check if this regular table overlaps with any native table
                    table_range = table["range"]
                    overlaps_with_native = False
                    
                    for native_table in native_tables:
                        table_props = native_table.get("tableProperties", {})
                        native_range = table_props.get("range", {})
                        
                        # Convert native range to A1 notation with validation
                        start_row = max(1, native_range.get("startRowIndex", 0) + 1)
                        start_col = max(1, native_range.get("startColumnIndex", 0) + 1)
                        
                        # Handle end indices properly for overlap detection
                        raw_end_row = native_range.get("endRowIndex", 0)
                        raw_end_col = native_range.get("endColumnIndex", 0)
                        
                        if raw_end_row <= 0:
                            end_row = start_row + 3  # Default to 4 rows
                        else:
                            end_row = raw_end_row
                        
                        if raw_end_col <= 0:
                            end_col = start_col + 4  # Default to 5 columns
                        else:
                            end_col = raw_end_col
                        
                        start_col_letter = col_to_letter(start_col)
                        end_col_letter = col_to_letter(end_col)
                        native_range_str = f"{start_col_letter}{start_row}:{end_col_letter}{end_row}"
                        
                        # Check for overlap using proper range intersection
                        if ranges_overlap(table_range, native_range_str):
                            overlaps_with_native = True
                            break
                    
                    if not overlaps_with_native:
                        non_overlapping_regular_tables.append(table)
                
                # Add non-overlapping regular tables
                for table in non_overlapping_regular_tables:
                    structures.append({
                        "structure_type": "regular_table",
                        "name": f"DataTable_{len([s for s in structures if s['structure_type'] == 'regular_table']) + 1}",
                        "range": table["range"],
                        "description": f"Regular data table with {table['rows']} rows and {table['columns']} columns"
                    })
                    summary["tables"] += 1
                
                # Detect scattered data areas (excluding all table areas)
                scattered_areas = _detect_scattered_data(values, non_overlapping_regular_tables, all_table_ranges)
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

def _detect_scattered_data(values, tables, all_table_ranges):
    """Detect scattered data areas (non-table areas)."""
    scattered_areas = []
    if not values:
        return scattered_areas
    
    # Find areas that are not part of any table (native or regular)
    current_area = None
    
    for row_idx, row in enumerate(values):
        if not row:
            continue
        
        # Check if this row has data outside of all tables
        has_scattered_data = False
        for col_idx, cell in enumerate(row):
            if cell and cell.strip():
                cell_range = f"{chr(65 + col_idx)}{row_idx + 1}"
                # Check if this cell is part of any table (native or regular)
                in_table = False
                for table_range in all_table_ranges:
                    if is_cell_in_range(cell_range, table_range):
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
            
            # Count cells in this row that are not in any table
            for col_idx, cell in enumerate(row):
                if cell and cell.strip():
                    cell_range = f"{chr(65 + col_idx)}{row_idx + 1}"
                    # Only count if not in any table
                    in_table = False
                    for table_range in all_table_ranges:
                        if is_cell_in_range(cell_range, table_range):
                            in_table = True
                            break
                    
                    if not in_table:
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

 