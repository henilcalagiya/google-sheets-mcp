from typing import Dict, Any, List
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.json_utils import compact_json_response

def list_spreadsheets(drive_service, max_results: int = 10) -> List[Dict[str, Any]]:
    """List all spreadsheets accessible to the user."""
    try:
        results = (
            drive_service.files()
            .list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=max_results,
                fields="files(id,name)",
            )
            .execute()
        )
        files = results.get("files", [])
        spreadsheet_infos = []
        for file in files:
            spreadsheet_infos.append({
                "name": file["name"],
            })
        return spreadsheet_infos
    except HttpError as error:
        raise RuntimeError(f"Error listing spreadsheets: {error}")

def list_all_spreadsheets_handler(
    drive_service,
    sheets_service,
    max_results: int = 10
) -> str:
    """Handler to list all spreadsheets accessible to the user."""
    spreadsheets = list_spreadsheets(drive_service, max_results)
    return compact_json_response({
        "spreadsheets": spreadsheets,
        "total_spreadsheets": len(spreadsheets),
        "message": f"Successfully listed {len(spreadsheets)} spreadsheets."
    }) 