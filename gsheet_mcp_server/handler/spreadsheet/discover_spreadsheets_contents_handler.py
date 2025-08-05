from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.json_utils import compact_json_response

def discover_spreadsheets_contents(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> Dict[str, Any]:
    """
    Discover and analyze all contents within spreadsheets including tables, charts, and other elements.
    
    This provides comprehensive discovery of all named and unnamed elements in spreadsheets.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        max_spreadsheets: Maximum number of spreadsheets to analyze
    
    Returns:
        Dictionary containing complete structure with all named elements and mentions of unnamed ones
    """
    try:
        # Get list of all spreadsheets
        drive_results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.spreadsheet'",
            pageSize=max_spreadsheets,
            fields="files(id,name)"
        ).execute()
        
        files = drive_results.get("files", [])
        
        result = {
            "total_spreadsheets": len(files),
            "spreadsheets": [],
            "total_sheets": 0,
            "total_tables": 0,
            "total_charts": 0,
            "total_other_elements": 0
        }
        
        for file in files:
            spreadsheet_name = file["name"]
            spreadsheet_id = file["id"]
            
            spreadsheet_info = {
                "name": spreadsheet_name,
                "sheets": [],
                "total_sheets": 0,
                "total_tables": 0,
                "total_charts": 0,
                "total_other_elements": 0
            }
            
            try:
                # Get complete sheet information including tables, charts, and other elements
                sheets_response = sheets_service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id,
                    fields="sheets.properties,sheets.charts,sheets.tables,sheets.slicers,sheets.developerMetadata,sheets.drawings"
                ).execute()
                
                sheets = sheets_response.get("sheets", [])
                
                for sheet in sheets:
                    props = sheet.get("properties", {})
                    sheet_name = props.get("title", "")
                    
                    if not sheet_name:
                        continue
                    
                    sheet_info = {
                        "name": sheet_name,
                        "tables": [],
                        "charts": [],
                        "other_elements": []
                    }
                    
                    # Extract table names
                    tables = sheet.get("tables", [])
                    for table in tables:
                        # Try different possible name fields for table names
                        table_name = table.get("displayName") or table.get("name") or f"Table{table.get('tableId', 'Unknown')}"
                        if table_name:
                            sheet_info["tables"].append(table_name)
                    
                    # Extract chart names
                    charts = sheet.get("charts", [])
                    for chart in charts:
                        spec = chart.get("spec", {})
                        chart_title = spec.get("title", "")
                        if chart_title:
                            sheet_info["charts"].append(chart_title)
                    
                    # Check for other elements
                    slicers = sheet.get("slicers", [])
                    drawings = sheet.get("drawings", [])
                    developer_metadata = sheet.get("developerMetadata", [])
                    
                    if slicers:
                        sheet_info["other_elements"].append(f"{len(slicers)} slicer(s)")
                    
                    if drawings:
                        sheet_info["other_elements"].append(f"{len(drawings)} drawing(s)")
                    
                    if developer_metadata:
                        sheet_info["other_elements"].append(f"{len(developer_metadata)} developer metadata item(s)")
                    
                    # Add sheet to spreadsheet info
                    spreadsheet_info["sheets"].append(sheet_info)
                    spreadsheet_info["total_sheets"] += 1
                    spreadsheet_info["total_tables"] += len(sheet_info["tables"])
                    spreadsheet_info["total_charts"] += len(sheet_info["charts"])
                    spreadsheet_info["total_other_elements"] += len(sheet_info["other_elements"])
                    
                    # Update global totals
                    result["total_sheets"] += 1
                    result["total_tables"] += len(sheet_info["tables"])
                    result["total_charts"] += len(sheet_info["charts"])
                    result["total_other_elements"] += len(sheet_info["other_elements"])
                
            except Exception as e:
                spreadsheet_info["error"] = str(e)
                spreadsheet_info["sheets"] = []
                print(f"Warning: Could not get complete structure for spreadsheet '{spreadsheet_name}': {e}")
            
            result["spreadsheets"].append(spreadsheet_info)
        
        result["message"] = f"Successfully retrieved complete structure of {len(result['spreadsheets'])} spreadsheets with {result['total_sheets']} sheets, {result['total_tables']} tables, {result['total_charts']} charts, and {result['total_other_elements']} other elements"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting complete spreadsheet structure: {str(e)}"
        }

def discover_spreadsheets_contents_handler(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> str:
    """
    Handler for discovering and analyzing all spreadsheet contents including all named and unnamed elements.
    """
    result = discover_spreadsheets_contents(
        drive_service=drive_service,
        sheets_service=sheets_service,
        max_spreadsheets=max_spreadsheets
    )
    return compact_json_response(result) 