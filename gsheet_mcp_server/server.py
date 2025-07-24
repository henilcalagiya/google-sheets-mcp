"""Google Sheets MCP Server implementation."""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Resource,
    TextContent,
    Tool,
    ToolParameter,
    ToolParameterType,
)
from pydantic import BaseModel


class GoogleSheetsMCPServer(Server):
    """MCP Server for Google Sheets integration."""

    def __init__(self, credentials_path: str):
        """Initialize the server with Google credentials."""
        super().__init__()
        self.credentials_path = credentials_path
        self.sheets_service = None
        self.drive_service = None
        self._setup_google_services()

    def _setup_google_services(self):
        """Set up Google Sheets and Drive API services."""
        try:
            # Try service account first
            credentials = ServiceAccountCredentials.from_service_account_file(
                self.credentials_path,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.readonly",
                ],
            )
        except Exception:
            # Fall back to OAuth2 credentials
            with open(self.credentials_path, "r") as f:
                creds_data = json.load(f)
            credentials = Credentials.from_authorized_user_info(creds_data)

        # Build the services
        self.sheets_service = build("sheets", "v4", credentials=credentials)
        self.drive_service = build("drive", "v3", credentials=credentials)

    async def initialize(
        self, client: "ClientSession", params: "InitializationOptions"
    ) -> None:
        """Initialize the server."""
        await super().initialize(client, params)

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools."""
        tools = [
            Tool(
                name="list_spreadsheets",
                description="List all accessible Google Sheets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10,
                        }
                    },
                },
            ),
            Tool(
                name="read_sheet",
                description="Read data from a specific Google Sheet",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "The ID of the spreadsheet",
                        },
                        "range": {
                            "type": "string",
                            "description": "The range to read (e.g., 'Sheet1!A1:D10')",
                            "default": "Sheet1!A1:Z1000",
                        },
                    },
                    "required": ["spreadsheet_id"],
                },
            ),
            Tool(
                name="write_sheet",
                description="Write data to a specific Google Sheet",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "The ID of the spreadsheet",
                        },
                        "range": {
                            "type": "string",
                            "description": "The range to write to (e.g., 'Sheet1!A1')",
                        },
                        "values": {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": "string"}},
                            "description": "The data to write (2D array)",
                        },
                    },
                    "required": ["spreadsheet_id", "range", "values"],
                },
            ),
            Tool(
                name="create_spreadsheet",
                description="Create a new Google Sheet",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the new spreadsheet",
                        },
                        "sheets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of sheet names to create",
                            "default": ["Sheet1"],
                        },
                    },
                    "required": ["title"],
                },
            ),
            Tool(
                name="search_sheets",
                description="Search for content within spreadsheets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]
        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls."""
        try:
            if request.name == "list_spreadsheets":
                return await self._list_spreadsheets(request.arguments)
            elif request.name == "read_sheet":
                return await self._read_sheet(request.arguments)
            elif request.name == "write_sheet":
                return await self._write_sheet(request.arguments)
            elif request.name == "create_spreadsheet":
                return await self._create_spreadsheet(request.arguments)
            elif request.name == "search_sheets":
                return await self._search_sheets(request.arguments)
            else:
                return CallToolResult(
                    isError=True,
                    content=[TextContent(type="text", text=f"Unknown tool: {request.name}")],
                )
        except Exception as e:
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
            )

    async def _list_spreadsheets(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List accessible spreadsheets."""
        max_results = arguments.get("max_results", 10)
        
        try:
            # Search for Google Sheets files
            results = (
                self.drive_service.files()
                .list(
                    q="mimeType='application/vnd.google-apps.spreadsheet'",
                    pageSize=max_results,
                    fields="files(id,name,createdTime,modifiedTime)",
                )
                .execute()
            )
            
            files = results.get("files", [])
            if not files:
                return CallToolResult(
                    content=[TextContent(type="text", text="No spreadsheets found.")]
                )
            
            # Format the results
            result_text = "Available spreadsheets:\n\n"
            for file in files:
                result_text += f"• {file['name']} (ID: {file['id']})\n"
                result_text += f"  Created: {file['createdTime']}\n"
                result_text += f"  Modified: {file['modifiedTime']}\n\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except HttpError as error:
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text=f"Error listing spreadsheets: {error}")],
            )

    async def _read_sheet(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Read data from a spreadsheet."""
        spreadsheet_id = arguments["spreadsheet_id"]
        range_name = arguments.get("range", "Sheet1!A1:Z1000")
        
        try:
            result = (
                self.sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            
            values = result.get("values", [])
            if not values:
                return CallToolResult(
                    content=[TextContent(type="text", text="No data found in the specified range.")]
                )
            
            # Format the data as a table
            result_text = f"Data from {range_name}:\n\n"
            for row in values:
                result_text += " | ".join(str(cell) for cell in row) + "\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except HttpError as error:
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text=f"Error reading sheet: {error}")],
            )

    async def _write_sheet(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Write data to a spreadsheet."""
        spreadsheet_id = arguments["spreadsheet_id"]
        range_name = arguments["range"]
        values = arguments["values"]
        
        try:
            body = {"values": values}
            result = (
                self.sheets_service.spreadsheets()
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
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Successfully updated {updated_cells} cells in {range_name}",
                    )
                ]
            )
            
        except HttpError as error:
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text=f"Error writing to sheet: {error}")],
            )

    async def _create_spreadsheet(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Create a new spreadsheet."""
        title = arguments["title"]
        sheets = arguments.get("sheets", ["Sheet1"])
        
        try:
            # Create the spreadsheet
            spreadsheet = {
                "properties": {"title": title},
                "sheets": [{"properties": {"title": sheet_name}} for sheet_name in sheets],
            }
            
            result = (
                self.sheets_service.spreadsheets()
                .create(body=spreadsheet)
                .execute()
            )
            
            spreadsheet_id = result["spreadsheetId"]
            spreadsheet_url = result["spreadsheetUrl"]
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Successfully created spreadsheet '{title}'\n"
                        f"ID: {spreadsheet_id}\n"
                        f"URL: {spreadsheet_url}",
                    )
                ]
            )
            
        except HttpError as error:
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text=f"Error creating spreadsheet: {error}")],
            )

    async def _search_sheets(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search for content within spreadsheets."""
        query = arguments["query"]
        max_results = arguments.get("max_results", 10)
        
        try:
            # First, get all spreadsheets
            results = (
                self.drive_service.files()
                .list(
                    q="mimeType='application/vnd.google-apps.spreadsheet'",
                    pageSize=max_results,
                    fields="files(id,name)",
                )
                .execute()
            )
            
            files = results.get("files", [])
            if not files:
                return CallToolResult(
                    content=[TextContent(type="text", text="No spreadsheets found to search.")]
                )
            
            # Search within each spreadsheet
            search_results = []
            for file in files:
                try:
                    # Get all sheets in the spreadsheet
                    spreadsheet = (
                        self.sheets_service.spreadsheets()
                        .get(spreadsheetId=file["id"])
                        .execute()
                    )
                    
                    for sheet in spreadsheet["sheets"]:
                        sheet_name = sheet["properties"]["title"]
                        range_name = f"{sheet_name}!A1:Z1000"
                        
                        # Read the sheet data
                        values_result = (
                            self.sheets_service.spreadsheets()
                            .values()
                            .get(spreadsheetId=file["id"], range=range_name)
                            .execute()
                        )
                        
                        values = values_result.get("values", [])
                        for row_idx, row in enumerate(values, 1):
                            for col_idx, cell in enumerate(row, 1):
                                if query.lower() in str(cell).lower():
                                    search_results.append({
                                        "spreadsheet": file["name"],
                                        "spreadsheet_id": file["id"],
                                        "sheet": sheet_name,
                                        "cell": f"{chr(64 + col_idx)}{row_idx}",
                                        "value": str(cell),
                                    })
                                    
                                    if len(search_results) >= max_results:
                                        break
                            if len(search_results) >= max_results:
                                break
                        if len(search_results) >= max_results:
                            break
                            
                except HttpError:
                    continue  # Skip spreadsheets we can't access
            
            if not search_results:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"No results found for '{query}'")]
                )
            
            # Format results
            result_text = f"Search results for '{query}':\n\n"
            for result in search_results:
                result_text += f"• {result['spreadsheet']} - {result['sheet']} {result['cell']}\n"
                result_text += f"  Value: {result['value']}\n\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except HttpError as error:
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text=f"Error searching sheets: {error}")],
            )

    async def list_resources(self, request: ListResourcesRequest) -> ListResourcesResult:
        """List available resources."""
        # For now, return empty list - could be extended to show recent sheets, etc.
        return ListResourcesResult(resources=[]) 