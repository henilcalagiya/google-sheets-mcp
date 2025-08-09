from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.json_utils import compact_json_response

def discover_spreadsheets(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> Dict[str, Any]:
    """
    Discover spreadsheets and their sheet names.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        max_spreadsheets: Maximum number of spreadsheets to analyze
    
    Returns:
        Dictionary containing spreadsheet names and their sheet names
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
            "total_sheets": 0
        }
        
        for file in files:
            spreadsheet_name = file["name"]
            spreadsheet_id = file["id"]
            
            spreadsheet_info = {
                "name": spreadsheet_name,
                "sheets": []
            }
            
            try:
                # Get only sheet properties (names)
                sheets_response = sheets_service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id,
                    fields="sheets.properties"
                ).execute()
                
                sheets = sheets_response.get("sheets", [])
                
                for sheet in sheets:
                    props = sheet.get("properties", {})
                    sheet_name = props.get("title", "")
                    
                    if sheet_name:
                        spreadsheet_info["sheets"].append(sheet_name)
                
                # Update totals
                result["total_sheets"] += len(spreadsheet_info["sheets"])
                
            except Exception as e:
                spreadsheet_info["error"] = str(e)
                spreadsheet_info["sheets"] = []
                print(f"Warning: Could not get sheets for spreadsheet '{spreadsheet_name}': {e}")
            
            result["spreadsheets"].append(spreadsheet_info)
        
        result["message"] = f"Successfully discovered {len(result['spreadsheets'])} spreadsheets with {result['total_sheets']} total sheets"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error discovering spreadsheets: {str(e)}"
        }

def discover_spreadsheets_handler(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> str:
    """
    Handler for discovering spreadsheets and their sheet names.
    """
    result = discover_spreadsheets(
        drive_service=drive_service,
        sheets_service=sheets_service,
        max_spreadsheets=max_spreadsheets
    )
    return compact_json_response(result)
