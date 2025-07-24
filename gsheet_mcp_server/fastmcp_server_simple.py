"""Google Sheets MCP Server using FastMCP - Simplified Version."""

import json
import os
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


class SpreadsheetInfo(BaseModel):
    """Spreadsheet information structure."""

    id: str = Field(description="Spreadsheet ID")
    name: str = Field(description="Spreadsheet name")
    created_time: str = Field(description="Creation time")
    modified_time: str = Field(description="Last modified time")
    url: str = Field(description="Spreadsheet URL")


class SheetInfo(BaseModel):
    """Sheet information structure."""

    sheet_id: int = Field(description="Sheet ID")
    title: str = Field(description="Sheet title")
    index: int = Field(description="Sheet index")
    grid_properties: Dict[str, Any] = Field(description="Grid properties (rows, columns)")


# Create an MCP server
mcp = FastMCP("Google Sheets")


def _setup_google_services(credentials_path: str):
    """Set up Google Sheets and Drive API services."""
    try:
        # Try service account first
        credentials = ServiceAccountCredentials.from_service_account_file(
            credentials_path,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly",
            ],
        )
    except Exception:
        # Fall back to OAuth2 credentials
        with open(credentials_path, "r") as f:
            creds_data = json.load(f)
        credentials = Credentials.from_authorized_user_info(creds_data)

    # Build the services
    sheets_service = build("sheets", "v4", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    return sheets_service, drive_service


# Initialize services
credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
if credentials_path:
    sheets_service, drive_service = _setup_google_services(credentials_path)
else:
    sheets_service = None
    drive_service = None


@mcp.tool()
def list_spreadsheets(max_results: int = 10) -> List[SpreadsheetInfo]:
    """List all accessible Google Sheets."""
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        # Search for Google Sheets files
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
        if not files:
            return []
        
        # Convert to structured output
        spreadsheet_infos = []
        for file in files:
            spreadsheet_infos.append(
                SpreadsheetInfo(
                    id=file["id"],
                    name=file["name"],
                    created_time=file["createdTime"],
                    modified_time=file["modifiedTime"],
                    url=file.get("webViewLink", ""),
                )
            )
        return spreadsheet_infos
        
    except HttpError as error:
        raise RuntimeError(f"Error listing spreadsheets: {error}")


@mcp.tool()
def list_sheets_in_spreadsheet(spreadsheet_id: str) -> List[SheetInfo]:
    """List all sheets in a specific Google Spreadsheet."""
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        # Get spreadsheet metadata
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties"
        ).execute()
        
        sheets = spreadsheet.get("sheets", [])
        if not sheets:
            return []
        
        sheet_infos = []
        for sheet in sheets:
            props = sheet["properties"]
            sheet_infos.append(
                SheetInfo(
                    sheet_id=props["sheetId"],
                    title=props["title"],
                    index=props["index"],
                    grid_properties={
                        "rowCount": props.get("gridProperties", {}).get("rowCount", 0),
                        "columnCount": props.get("gridProperties", {}).get("columnCount", 0)
                    }
                )
            )
        
        return sheet_infos
        
    except HttpError as error:
        raise RuntimeError(f"Error listing sheets: {error}")


@mcp.tool()
def modify_sheets_in_spreadsheet(
    spreadsheet_id: str,
    add_sheet_names: Optional[List[str]] = None,
    delete_sheet_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Add and/or delete sheets in a Google Spreadsheet.
    - add_sheet_names: list of sheet names to add (optional)
    - delete_sheet_ids: list of sheet IDs to delete (optional)
    Returns a dict with keys: 'added', 'deleted', 'message'.
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not add_sheet_names and not delete_sheet_ids:
        raise ValueError("At least one of add_sheet_names or delete_sheet_ids must be provided.")
    added_sheets = []
    deleted_ids = []
    requests = []
    # Prepare add requests
    if add_sheet_names:
        for sheet_name in add_sheet_names:
            requests.append({
                "addSheet": {
                    "properties": {
                        "title": sheet_name
                    }
                }
            })
    # Prepare delete requests
    if delete_sheet_ids:
        for sheet_id in delete_sheet_ids:
            requests.append({
                "deleteSheet": {
                    "sheetId": sheet_id
                }
            })
            deleted_ids.append(sheet_id)
    try:
        if requests:
            body = {"requests": requests}
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
        # If sheets were added, get their info
        if add_sheet_names:
            updated_spreadsheet = sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields="sheets.properties"
            ).execute()
            for sheet in updated_spreadsheet.get("sheets", []):
                props = sheet["properties"]
                if props["title"] in add_sheet_names:
                    added_sheets.append(
                        SheetInfo(
                            sheet_id=props["sheetId"],
                            title=props["title"],
                            index=props["index"],
                            grid_properties={
                                "rowCount": props.get("gridProperties", {}).get("rowCount", 0),
                                "columnCount": props.get("gridProperties", {}).get("columnCount", 0)
                            }
                        )
                    )
        msg = []
        if added_sheets:
            msg.append(f"Added {len(added_sheets)} sheet(s)")
        if deleted_ids:
            msg.append(f"Deleted {len(deleted_ids)} sheet(s)")
        if not msg:
            msg.append("No changes made.")
        return {
            "added": [s.dict() for s in added_sheets],
            "deleted": deleted_ids,
            "message": ", ".join(msg)
        }
    except HttpError as error:
        raise RuntimeError(f"Error modifying sheets: {error}")


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    return f"Hello, {name}! Welcome to Google Sheets MCP Server."


# Add a spreadsheet info resource
@mcp.resource("spreadsheet://{spreadsheet_id}")
def get_spreadsheet_info(spreadsheet_id: str) -> str:
    """Get information about a specific spreadsheet."""
    if not sheets_service:
        return "Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH."
    
    try:
        result = (
            sheets_service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()
        )
        
        title = result.get("properties", {}).get("title", "Unknown")
        sheets_count = len(result.get("sheets", []))
        
        return f"Spreadsheet: {title}\nSheets: {sheets_count}\nID: {spreadsheet_id}"
        
    except HttpError as error:
        return f"Error getting spreadsheet info: {error}"


# Add prompts
@mcp.prompt()
def analyze_spreadsheet(spreadsheet_id: str, analysis_type: str = "summary") -> str:
    """Generate prompts for analyzing spreadsheet data."""
    return f"""Analyze the spreadsheet with ID {spreadsheet_id}.

Analysis type: {analysis_type}

Please provide insights about:
- Data structure and organization
- Key metrics and trends
- Potential improvements
- Data quality issues

Use the available tools to gather information about this spreadsheet."""


@mcp.prompt()
def create_report(spreadsheet_id: str, report_type: str = "basic") -> str:
    """Generate prompts for creating reports."""
    return f"""Create a {report_type} report for spreadsheet {spreadsheet_id}.

Please include:
- Executive summary
- Key findings
- Data visualizations (if applicable)
- Recommendations

Use the available tools to access the spreadsheet data."""


if __name__ == "__main__":
    mcp.run() 