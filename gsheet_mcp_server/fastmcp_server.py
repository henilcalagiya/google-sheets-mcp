"""Google Sheets MCP Server using FastMCP."""

import json
import os
from typing import Any, Dict, List

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


class SearchResult(BaseModel):
    """Search result structure."""

    spreadsheet: str = Field(description="Spreadsheet name")
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet: str = Field(description="Sheet name")
    cell: str = Field(description="Cell reference")
    value: str = Field(description="Cell value")


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
def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1!A1:Z1000") -> str:
    """Read data from a specific Google Sheet."""
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        result = (
            sheets_service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        
        values = result.get("values", [])
        if not values:
            return "No data found in the specified range."
        
        # Format the data as a table
        result_text = f"Data from {range_name}:\n\n"
        for row in values:
            result_text += " | ".join(str(cell) for cell in row) + "\n"
        
        return result_text
        
    except HttpError as error:
        raise RuntimeError(f"Error reading sheet: {error}")


@mcp.tool()
def write_sheet(spreadsheet_id: str, range_name: str, values: List[List[str]]) -> str:
    """Write data to a specific Google Sheet."""
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        body = {"values": values}
        result = (
            sheets_service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )
        
        updated_cells = result.get("updatedCells", 0)
        return f"Successfully updated {updated_cells} cells in {range_name}"
        
    except HttpError as error:
        raise RuntimeError(f"Error writing to sheet: {error}")


@mcp.tool()
def create_spreadsheet(title: str, sheets: List[str] = None) -> SpreadsheetInfo:
    """Create a new Google Sheet."""
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    if sheets is None:
        sheets = ["Sheet1"]
    
    try:
        # Create the spreadsheet
        spreadsheet = {
            "properties": {"title": title},
            "sheets": [{"properties": {"title": sheet_name}} for sheet_name in sheets],
        }
        
        result = (
            sheets_service.spreadsheets()
            .create(body=spreadsheet)
            .execute()
        )
        
        return SpreadsheetInfo(
            id=result["spreadsheetId"],
            name=title,
            created_time="",  # Not available in create response
            modified_time="",  # Not available in create response
            url=result["spreadsheetUrl"],
        )
        
    except HttpError as error:
        raise RuntimeError(f"Error creating spreadsheet: {error}")


@mcp.tool()
def search_sheets(query: str, max_results: int = 10) -> List[SearchResult]:
    """Search for content within spreadsheets."""
    if not drive_service or not sheets_service:
        raise RuntimeError("Google services not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    try:
        # First, get all spreadsheets
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
        if not files:
            return []
        
        # Search within each spreadsheet
        search_results = []
        for file in files:
            try:
                # Get all sheets in the spreadsheet
                spreadsheet = (
                    sheets_service.spreadsheets()
                    .get(spreadsheetId=file["id"])
                    .execute()
                )
                
                for sheet in spreadsheet["sheets"]:
                    sheet_name = sheet["properties"]["title"]
                    range_name = f"{sheet_name}!A1:Z1000"
                    
                    # Read the sheet data
                    values_result = (
                        sheets_service.spreadsheets()
                        .values()
                        .get(spreadsheetId=file["id"], range=range_name)
                        .execute()
                    )
                    
                    values = values_result.get("values", [])
                    for row_idx, row in enumerate(values, 1):
                        for col_idx, cell in enumerate(row, 1):
                            if query.lower() in str(cell).lower():
                                search_results.append(
                                    SearchResult(
                                        spreadsheet=file["name"],
                                        spreadsheet_id=file["id"],
                                        sheet=sheet_name,
                                        cell=f"{chr(64 + col_idx)}{row_idx}",
                                        value=str(cell),
                                    )
                                )
                                
                                if len(search_results) >= max_results:
                                    break
                        if len(search_results) >= max_results:
                            break
                    if len(search_results) >= max_results:
                        break
                        
            except HttpError:
                continue  # Skip spreadsheets we can't access
        
        return search_results
        
    except HttpError as error:
        raise RuntimeError(f"Error searching sheets: {error}")


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


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! Welcome to Google Sheets MCP Server."


# Add a spreadsheet resource
@mcp.resource("spreadsheet://{spreadsheet_id}")
def get_spreadsheet_info(spreadsheet_id: str) -> str:
    """Get information about a specific spreadsheet"""
    if not sheets_service:
        return "Google Sheets service not initialized"
    
    try:
        result = (
            sheets_service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()
        )
        
        properties = result["properties"]
        return f"Spreadsheet: {properties['title']}\nID: {spreadsheet_id}\nSheets: {len(result['sheets'])}"
        
    except HttpError:
        return f"Could not access spreadsheet {spreadsheet_id}"


# Add prompts
@mcp.prompt()
def analyze_spreadsheet(spreadsheet_id: str, analysis_type: str = "summary") -> str:
    """Generate a prompt for analyzing spreadsheet data"""
    analysis_prompts = {
        "summary": "Please provide a summary of the data in this spreadsheet",
        "trends": "Please analyze the trends in this spreadsheet data",
        "insights": "Please provide key insights from this spreadsheet data",
        "recommendations": "Please provide recommendations based on this spreadsheet data",
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts["summary"])
    return f"{prompt} for spreadsheet {spreadsheet_id}."


@mcp.prompt()
def create_report(spreadsheet_id: str, report_type: str = "basic") -> str:
    """Generate a prompt for creating a report from spreadsheet data"""
    return f"Please create a {report_type} report based on the data in spreadsheet {spreadsheet_id}."


if __name__ == "__main__":
    mcp.run() 