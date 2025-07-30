from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.handler.list_spreadsheets_handler import list_spreadsheets
from gsheet_mcp_server.handler.list_sheets_handler import list_sheets
from gsheet_mcp_server.helper.json_utils import compact_json_response



def get_spreadsheet_overview(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> Dict[str, Any]:
    """
    Get a comprehensive overview of all spreadsheets with their sheets.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        max_spreadsheets: Maximum number of spreadsheets to analyze
    
    Returns:
        Dictionary containing overview of all spreadsheets
    """
    try:
        # Get list of all spreadsheets
        spreadsheets = list_spreadsheets(drive_service, max_spreadsheets)
        
        overview = {
            "total_spreadsheets": len(spreadsheets),
            "spreadsheets": []
        }
        
        for spreadsheet in spreadsheets:
            spreadsheet_name = spreadsheet["name"]
            
            # Get spreadsheet ID
            spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
            if not spreadsheet_id:
                continue
            
            # Get basic spreadsheet info
            spreadsheet_info = {
                "name": spreadsheet_name,
                "id": spreadsheet_id,
                "sheets": []
            }
            
            try:
                # Get all sheets in this spreadsheet
                sheet_infos = list_sheets(sheets_service, spreadsheet_id)
                
                for sheet_info in sheet_infos:
                    sheet_data = {
                        "name": sheet_info.title,
                        "index": sheet_info.index,
                        "grid_properties": sheet_info.grid_properties
                    }
                    
                    spreadsheet_info["sheets"].append(sheet_data)
                
                # Add summary for this spreadsheet
                spreadsheet_info["total_sheets"] = len(spreadsheet_info["sheets"])
                
            except Exception as e:
                spreadsheet_info["error"] = str(e)
                spreadsheet_info["sheets"] = []
            
            overview["spreadsheets"].append(spreadsheet_info)
        
        # Add overall summary
        total_sheets = sum(spreadsheet.get("total_sheets", 0) for spreadsheet in overview["spreadsheets"])
        overview["total_sheets"] = total_sheets
        
        overview["message"] = f"Successfully analyzed {len(overview['spreadsheets'])} spreadsheets with {total_sheets} total sheets"
        
        return overview
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting spreadsheets overview: {str(e)}"
        }


def get_spreadsheets_overview_handler(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> str:
    """
    Handler for getting comprehensive overview of all spreadsheets.
    """
    overview = get_spreadsheet_overview(
        drive_service=drive_service,
        sheets_service=sheets_service,
        max_spreadsheets=max_spreadsheets
    )
    return compact_json_response(overview) 