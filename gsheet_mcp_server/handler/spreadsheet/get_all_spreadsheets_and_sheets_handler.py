from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.json_utils import compact_json_response

def get_all_spreadsheets_and_sheets(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> Dict[str, Any]:
    """
    Get all spreadsheets and their sheets in a simple, clean way.
    
    This tool efficiently retrieves just spreadsheet names and sheet names
    using minimal API calls for optimal performance.
    
    Args:
        drive_service: Google Drive service
        sheets_service: Google Sheets service
        max_spreadsheets: Maximum number of spreadsheets to analyze
    
    Returns:
        Dictionary containing spreadsheets with just their sheet names
    """
    try:
        # Get list of all spreadsheets directly (single API call)
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
            
            # Get sheets for this spreadsheet (single API call per spreadsheet)
            spreadsheet_info = {
                "name": spreadsheet_name,
                "sheets": [],
                "total_sheets": 0
            }
            
            try:
                # Get sheets with only title field for maximum efficiency
                sheets_response = sheets_service.spreadsheets().get(
                    spreadsheetId=spreadsheet_id,
                    fields="sheets.properties(title)"
                ).execute()
                
                sheets = sheets_response.get("sheets", [])
                for sheet in sheets:
                    props = sheet.get("properties", {})
                    sheet_name = props.get("title", "")
                    
                    if sheet_name:  # Only add non-empty sheet names
                        spreadsheet_info["sheets"].append(sheet_name)
                
                spreadsheet_info["total_sheets"] = len(spreadsheet_info["sheets"])
                result["total_sheets"] += spreadsheet_info["total_sheets"]
                
            except Exception as e:
                spreadsheet_info["error"] = str(e)
                spreadsheet_info["sheets"] = []
                print(f"Warning: Could not get sheets for spreadsheet '{spreadsheet_name}': {e}")
            
            result["spreadsheets"].append(spreadsheet_info)
        
        result["message"] = f"Successfully retrieved {len(result['spreadsheets'])} spreadsheets with {result['total_sheets']} total sheets"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting spreadsheets and sheets: {str(e)}"
        }

def get_all_spreadsheets_and_sheets_handler(
    drive_service,
    sheets_service,
    max_spreadsheets: int = 10
) -> str:
    """
    Handler for getting all spreadsheets and their sheets efficiently.
    """
    result = get_all_spreadsheets_and_sheets(
        drive_service=drive_service,
        sheets_service=sheets_service,
        max_spreadsheets=max_spreadsheets
    )
    return compact_json_response(result) 