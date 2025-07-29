from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name, get_sheet_ids_by_names

def insert_dimension(
    sheets_service, 
    spreadsheet_id: str, 
    sheet_id: int, 
    dimension: str, 
    position: int, 
    count: int
) -> Dict[str, Any]:
    """Insert rows or columns in a Google Sheet."""
    try:
        # Calculate start and end indices from position and count
        start_index = position
        end_index = position + count
        
        # Prepare the batch update request
        request = {
            'insertDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': dimension,  # 'ROWS' or 'COLUMNS'
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'inheritFromBefore': True
            }
        }
        
        result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [request]}
        ).execute()
        
        return {
            "success": True,
            "dimension": dimension,
            "position": position,
            "count": count,
            "start_index": start_index,
            "end_index": end_index
        }
        
    except HttpError as error:
        raise RuntimeError(f"Error inserting {dimension.lower()}: {error}")

def insert_dimension_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    dimension: str,
    position: int,
    count: int
) -> Dict[str, Any]:
    """Handler to insert rows or columns in a sheet."""
    
    # Validate input
    if not sheet_name:
        return {
            "success": False,
            "message": "No sheet name provided."
        }
    
    if dimension not in ['ROWS', 'COLUMNS']:
        return {
            "success": False,
            "message": "Dimension must be 'ROWS' or 'COLUMNS'."
        }
    
    if position < 0:
        return {
            "success": False,
            "message": "Position must be >= 0."
        }
    
    if count <= 0:
        return {
            "success": False,
            "message": "Count must be > 0."
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
        # Insert the dimension
        result = insert_dimension(sheets_service, spreadsheet_id, sheet_id, dimension, position, count)
        
        dimension_name = dimension.lower()
        dimension_plural = f"{dimension_name}s" if dimension == 'ROWS' else f"{dimension_name}s"
        
        return {
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "dimension": dimension,
            "position": position,
            "count": count,
            "dimensions_inserted": count,
            "message": f"Successfully inserted {count} {dimension_name}(s) at position {position} in sheet '{sheet_name}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error inserting {dimension.lower()}: {str(e)}"
        } 