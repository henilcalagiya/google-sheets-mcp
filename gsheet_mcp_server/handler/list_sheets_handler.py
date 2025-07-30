from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.models import SheetInfo
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response

def list_sheets(sheets_service, spreadsheet_id: str) -> List[SheetInfo]:
    try:
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties"
        ).execute()
        sheets = spreadsheet.get("sheets", [])
        return [
            SheetInfo(
                sheet_id=props["sheetId"],
                title=props["title"],
                index=props["index"],
                grid_properties={
                    "rowCount": props.get("gridProperties", {}).get("rowCount", 0),
                    "columnCount": props.get("gridProperties", {}).get("columnCount", 0)
                }
            )
            for sheet in sheets
            for props in [sheet["properties"]]
        ]
    except HttpError as error:
        raise RuntimeError(f"Error listing sheets: {error}")

def list_sheets_handler(
    drive_service,
    sheets_service,
    spreadsheet_name: str
) -> str:
    """Handler to list all sheets in a spreadsheet."""
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    if not spreadsheet_id:
        return compact_json_response({
            "success": False,
            "message": f"Spreadsheet '{spreadsheet_name}' not found."
        })
    
    try:
        sheet_infos = list_sheets(sheets_service, spreadsheet_id)
        
        # Create response without sheet IDs
        sheets_data = []
        for sheet in sheet_infos:
            sheets_data.append({
                "title": sheet.title,
                "index": sheet.index,
                "grid_properties": sheet.grid_properties
            })
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheets": sheets_data,
            "total_sheets": len(sheet_infos),
            "message": f"Successfully listed {len(sheet_infos)} sheets in '{spreadsheet_name}'"
        })
    except Exception as e:
        return compact_json_response({
            "success": False,
            "message": f"Error listing sheets: {str(e)}"
        }) 