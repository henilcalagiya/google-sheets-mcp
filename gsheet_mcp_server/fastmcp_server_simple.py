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
from .handler.all_spreadsheet_management_handler import all_spreadsheet_management_handler
from .handler.sheets_management_handler import sheets_management_handler
from .models import SpreadsheetInfo, SheetInfo


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


# Remove the list_spreadsheets tool function (from @mcp.tool() def list_spreadsheets ... to its end)


@mcp.tool()
def all_spreadsheet_management_tool(
    spreadsheet_id: str = "",
    new_title: str = "",
    max_results: int = 10
) -> Dict[str, Any]:
    """Combined tool: List all spreadsheets and optionally rename a spreadsheet by ID.
    - If spreadsheet_id and new_title are provided, renames the spreadsheet.
    - Always returns the list of spreadsheets after any operation.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return all_spreadsheet_management_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_id=spreadsheet_id,
        new_title=new_title,
        max_results=max_results
    )


@mcp.tool()
def sheets_management_tool(
    spreadsheet_id: str,
    add_sheet_names: Optional[List[str]] = None,
    delete_sheet_ids: Optional[List[int]] = None,
    rename_sheets: Optional[Dict[int, str]] = None
) -> Dict[str, Any]:
    """Manage sheets in a Google Spreadsheet: list, create (add), delete, and/or rename sheets.
    - If none of add_sheet_names, delete_sheet_ids, or rename_sheets is provided, lists all sheets.
    - add_sheet_names: list of sheet names to create/add as new sheets (optional) or must pass empty list
    - delete_sheet_ids: list of sheet IDs to delete (optional) or must pass empty list
    - rename_sheets: To rename sheets, pass a dict mapping sheet IDs to new titles; otherwise, pass an empty dict.
    Returns a dict with keys: 'sheets' (list of SheetInfo), 'added', 'deleted', 'renamed', 'message'.
    """

    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return sheets_management_handler(
        sheets_service=sheets_service,
        spreadsheet_id=spreadsheet_id,
        add_sheet_names=add_sheet_names,
        delete_sheet_ids=delete_sheet_ids,
        rename_sheets_map=rename_sheets
    )


if __name__ == "__main__":
    mcp.run() 