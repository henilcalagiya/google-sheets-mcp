from typing import List, Dict, Any, Optional
from googleapiclient.errors import HttpError
from gsheet_mcp_server.models import SpreadsheetInfo, SheetInfo

def list_spreadsheets(drive_service, max_results: int = 10) -> List[Dict[str, Any]]:
    """List all spreadsheets accessible to the user."""
    try:
        results = (
            drive_service.files()
            .list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=max_results,
                fields="files(id,name,createdTime,modifiedTime,webViewLink)",
            )
            .execute()
        )
        files = results.get("files", [])
        spreadsheet_infos = []
        for file in files:
            spreadsheet_infos.append({
                "name": file["name"],
                "created_time": file["createdTime"],
                "modified_time": file["modifiedTime"],
                "url": file.get("webViewLink", ""),
            })
        return spreadsheet_infos
    except HttpError as error:
        raise RuntimeError(f"Error listing spreadsheets: {error}")

def rename_spreadsheet(sheets_service, spreadsheet_id: str, new_title: str) -> str:
    """Rename a spreadsheet by its ID."""
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "updateSpreadsheetProperties": {
                            "properties": {"title": new_title},
                            "fields": "title"
                        }
                    }
                ]
            }
        ).execute()
        return f"Spreadsheet {spreadsheet_id} renamed to '{new_title}'"
    except HttpError as error:
        raise RuntimeError(f"Error renaming spreadsheet: {error}")

def add_sheets(sheets_service, spreadsheet_id: str, sheet_names: List[str]) -> List[SheetInfo]:
    requests = [
        {"addSheet": {"properties": {"title": name}}} for name in sheet_names
    ]
    if not requests:
        return []
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise RuntimeError(f"Error adding sheets: {error}")
    return []  # Info will be fetched after

def delete_sheets(sheets_service, spreadsheet_id: str, sheet_ids: List[int]) -> List[int]:
    requests = [
        {"deleteSheet": {"sheetId": sheet_id}} for sheet_id in sheet_ids
    ]
    if not requests:
        return []
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise RuntimeError(f"Error deleting sheets: {error}")
    return sheet_ids



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

def rename_sheets(sheets_service, spreadsheet_id: str, sheet_ids: List[int], new_titles: List[str]) -> List[str]:
    requests = [
        {"updateSheetProperties": {"properties": {"sheetId": sheet_id, "title": new_title}, "fields": "title"}}
        for sheet_id, new_title in zip(sheet_ids, new_titles)
    ]
    if not requests:
        return []
    try:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except HttpError as error:
        raise RuntimeError(f"Error renaming sheets: {error}")
    return [f"Sheet {sheet_id} renamed to '{new_title}'" for sheet_id, new_title in zip(sheet_ids, new_titles)]

