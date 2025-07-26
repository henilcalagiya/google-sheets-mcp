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
from .handler.spreadsheet_management_handler import spreadsheet_management_handler
from .handler.sheet_management_handler import sheet_management_handler
from .models import SpreadsheetInfo, SheetInfo
from .handler.rename_sheets_handler import rename_sheets_handler
from .handler.read_sheet_data_handler import read_multiple_ranges, get_sheet_metadata
from .handler.write_cell_handler import write_cell_data
from .handler.write_row_handler import write_row_data
from .handler.write_grid_handler import write_grid_data
from .handler.append_data_handler import append_data_to_column
from .handler.clear_range_handler import clear_range_data
from .handler.find_replace_handler import find_replace_text
from .handler.insert_rows_handler import insert_rows_data
from .handler.delete_rows_handler import delete_rows_data
from .handler.insert_columns_handler import insert_columns_data
from .handler.delete_columns_handler import delete_columns_data
from .handler.move_rows_handler import move_rows_data
from .handler.resize_columns_handler import resize_columns_data
from .handler.format_cells_handler import format_cells_data
from .handler.conditional_format_handler import conditional_format_data
from .handler.merge_cells_handler import merge_cells_data
from .handler.create_data_table_handler import create_data_table
from .handler.read_sheet_data_handler import read_multiple_ranges


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
def spreadsheet_management_tool(
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
    return spreadsheet_management_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_id=spreadsheet_id,
        new_title=new_title,
        max_results=max_results
    )




@mcp.tool()
def sheet_management_tool(
    spreadsheet_name: str = Field(..., description="Required: The name of the Google Spreadsheet"),
    add_sheet_names: Optional[List[str]] = Field(default_factory=list, description="Optional: List of sheet names to add as new sheets. Pass an empty list if not adding."),
    delete_sheet_ids: Optional[List[int]] = Field(default_factory=list, description="Optional: List of sheet IDs to delete. Pass an empty list if not deleting."),
    include_metadata: bool = Field(default=True, description="Optional: Whether to include detailed metadata. Set to False for faster response with basic info only."),
    target_sheet_names: Optional[List[str]] = Field(default_factory=list, description="Optional: List of specific sheet names to get metadata for. If provided, only returns metadata for these sheets. If empty list, returns metadata for all sheets.")
) -> Dict[str, Any]:
    """Sheet management with metadata support.
    
    This tool combines sheet management operations (add/delete/list) with detailed metadata.
    
    Features:
    - List all sheets with basic info
    - Add new sheets
    - Delete existing sheets
    - Include detailed metadata (optional)
    - Focus metadata on specific sheets (optional)
    
    Examples:
    - List all sheets with metadata: include_metadata=True, target_sheet_names=[]
    - Focus on specific sheet: target_sheet_names=["Sheet1"]
    - Focus on multiple sheets: target_sheet_names=["Sheet1", "Sheet2", "Data"]
    - Fast operation: include_metadata=False
    - Add sheets with metadata: add_sheet_names=["NewSheet"], include_metadata=True
    
    Returns a dict with keys: 'sheets', 'added', 'deleted', 'metadata', 'operations_performed', 'message'.
    """

    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return sheet_management_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        add_sheet_names=add_sheet_names,
        delete_sheet_ids=delete_sheet_ids,
        include_metadata=include_metadata,
        target_sheet_names=target_sheet_names
    )

@mcp.tool()
def rename_sheets_tool(
    spreadsheet_name: str = Field(..., description="must pass the spreadsheet name"),
    sheet_ids: List[int] = Field(..., description="Required: List of sheet IDs to rename"),
    new_titles: List[str] = Field(..., description="Required: List of new titles for the sheets")
) -> Dict[str, Any]:
    """
    Rename sheets in a Google Spreadsheet.
    - spreadsheet_name: must pass the spreadsheet name
    - sheet_ids: list of sheet IDs to rename
    - new_titles: list of new titles for the sheets
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return rename_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_ids=sheet_ids,
        new_titles=new_titles
    )



@mcp.tool()
def read_sheet_data_tool(
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet"),
    ranges: List[str] = Field(..., description="List of range strings (e.g., ['Sheet1!A1:B10', 'Sheet2!A:A'])"),
    value_render_option: str = Field(default="FORMATTED_VALUE", description="How to render values: FORMATTED_VALUE, UNFORMATTED_VALUE, or FORMULA"),
    date_time_render_option: str = Field(default="FORMATTED_STRING", description="How to render dates: SERIAL_NUMBER or FORMATTED_STRING")
) -> Dict[str, Any]:
    """
    Read sheet data with flexible range support - single or multiple ranges in one efficient API call.
    
    Examples:
    - Single column: ['Sheet1!A:A']
    - Multiple columns: ['Sheet1!A:A', 'Sheet1!B:B', 'Sheet1!C:C']
    - Custom ranges: ['Sheet1!A1:B10', 'Sheet2!A:A']
    - Cross-sheet: ['Sheet1!A:A', 'Sheet2!B:B', 'Sheet3!C:C']
    - Single cells: ['Sheet1!A1', 'Sheet1!B1', 'Sheet1!C1']
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return read_multiple_ranges(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        ranges=ranges,
        value_render_option=value_render_option,
        date_time_render_option=date_time_render_option
    )


@mcp.tool()
def write_cell(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    cell: str = Field(..., description="Cell reference (e.g., 'Sheet1!A1', 'Sheet2!B5')"),
    value: str = Field(..., description="Value to write to the cell")
) -> Dict[str, Any]:
    """
    Write a single value to a specific cell in Google Sheets.
    
    Examples:
    - Write text: cell='Sheet1!A1', value='Hello World'
    - Write formula: cell='Sheet1!A1', value='=SUM(B1:B10)'
    - Write number: cell='Sheet1!B1', value='42'
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return write_cell_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        cell=cell,
        value=value
    )


@mcp.tool()
def write_row(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    row_range: str = Field(..., description="Row range (e.g., 'Sheet1!A1:E1', 'Sheet1!1:1')"),
    values: List[str] = Field(..., description="List of values to write to the row")
) -> Dict[str, Any]:
    """
    Write values to a single row in Google Sheets.
    
    Examples:
    - Write headers: row_range='Sheet1!A1:E1', values=['Name', 'Email', 'Phone', 'Age', 'City']
    - Write data row: row_range='Sheet1!A2:E2', values=['John', 'john@email.com', '123-456-7890', '30', 'New York']
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return write_row_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        row_range=row_range,
        values=values
    )


@mcp.tool()
def write_grid(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    grid_range: str = Field(..., description="Grid range (e.g., 'Sheet1!A1:C5', 'Sheet1!A1:Z100')"),
    values: List[List[str]] = Field(..., description="2D array of values to write to the grid")
) -> Dict[str, Any]:
    """
    Write a 2D grid of values to a range in Google Sheets.
    
    Examples:
    - Write table: grid_range='Sheet1!A1:C3', values=[['Name', 'Email', 'Phone'], ['John', 'john@email.com', '123'], ['Jane', 'jane@email.com', '456']]
    - Write large grid: grid_range='Sheet1!A1:Z100', values=[[...]] (100 rows of 26 columns each)
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return write_grid_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        grid_range=grid_range,
        values=values
    )


@mcp.tool()
def append_data(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    column_range: str = Field(..., description="Column range to append to (e.g., 'Sheet1!A:A', 'Sheet1!B:B')"),
    values: List[str] = Field(..., description="List of values to append to the column")
) -> Dict[str, Any]:
    """
    Append values to the end of a column in Google Sheets.
    
    Examples:
    - Append names: column_range='Sheet1!A:A', values=['Alice', 'Bob', 'Charlie']
    - Append emails: column_range='Sheet1!B:B', values=['alice@email.com', 'bob@email.com', 'charlie@email.com']
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return append_data_to_column(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        column_range=column_range,
        values=values
    )


@mcp.tool()
def clear_range(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    range_to_clear: str = Field(..., description="Range to clear (e.g., 'Sheet1!A1:B10', 'Sheet1!A:A')")
) -> Dict[str, Any]:
    """
    Clear all values from a range in Google Sheets (keeps formatting).
    
    Examples:
    - Clear cells: range_to_clear='Sheet1!A1:B10'
    - Clear column: range_to_clear='Sheet1!A:A'
    - Clear row: range_to_clear='Sheet1!1:1'
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return clear_range_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        range=range_to_clear
    )


@mcp.tool()
def find_replace(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    search_range: str = Field(..., description="Range to search in (e.g., 'Sheet1!A:A', 'Sheet1!A1:Z100')"),
    find_text: str = Field(..., description="Text to find"),
    replace_text: str = Field(..., description="Text to replace with"),
    match_case: bool = Field(default=False, description="Whether to match case (default: False)")
) -> Dict[str, Any]:
    """
    Find and replace text in a range in Google Sheets.
    
    Examples:
    - Replace text: search_range='Sheet1!A:A', find_text='old', replace_text='new'
    - Case sensitive: search_range='Sheet1!A1:Z100', find_text='OLD', replace_text='NEW', match_case=True
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return find_replace_text(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        search_range=search_range,
        find_text=find_text,
        replace_text=replace_text
    )


@mcp.tool()
def insert_rows(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)"),
    start_index: int = Field(..., description="Starting row index (0-based)"),
    end_index: int = Field(..., description="Ending row index (0-based, exclusive)")
) -> Dict[str, Any]:
    """
    Insert rows in a Google Sheet.
    
    Examples:
    - Insert 1 row: start_index=5, end_index=6
    - Insert 3 rows: start_index=10, end_index=13
    - Insert at beginning: start_index=0, end_index=1
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_id=sheet_id,
        start_index=start_index,
        end_index=end_index
    )


@mcp.tool()
def delete_rows(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)"),
    row_indices: List[int] = Field(..., description="List of row indices to delete (0-based)")
) -> Dict[str, Any]:
    """
    Delete entire rows from a Google Sheet.
    
    Examples:
    - Delete single row: row_indices=[5]
    - Delete multiple rows: row_indices=[1, 3, 5]
    - Delete first row: row_indices=[0]
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return delete_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_id=sheet_id,
        row_indices=row_indices
    )


@mcp.tool()
def insert_columns(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)"),
    start_index: int = Field(..., description="Starting column index (0-based)"),
    end_index: int = Field(..., description="Ending column index (0-based, exclusive)")
) -> Dict[str, Any]:
    """
    Insert columns in a Google Sheet.
    
    Examples:
    - Insert 1 column: start_index=2, end_index=3
    - Insert 3 columns: start_index=5, end_index=8
    - Insert at beginning: start_index=0, end_index=1
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return insert_columns_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_id=sheet_id,
        start_index=start_index,
        end_index=end_index
    )


@mcp.tool()
def delete_columns(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)"),
    column_indices: List[int] = Field(..., description="List of column indices to delete (0-based)")
) -> Dict[str, Any]:
    """
    Delete entire columns from a Google Sheet.
    
    Examples:
    - Delete single column: column_indices=[2]
    - Delete multiple columns: column_indices=[1, 3, 5]
    - Delete first column: column_indices=[0]
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return delete_columns_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_id=sheet_id,
        column_indices=column_indices
    )


@mcp.tool()
def move_rows(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)"),
    source_start_index: int = Field(..., description="Starting row index to move (0-based)"),
    source_end_index: int = Field(..., description="Ending row index to move (0-based, exclusive)"),
    destination_index: int = Field(..., description="Destination row index (0-based)")
) -> Dict[str, Any]:
    """
    Move rows in a Google Sheet.
    
    Examples:
    - Move 1 row: source_start_index=5, source_end_index=6, destination_index=10
    - Move 3 rows: source_start_index=10, source_end_index=13, destination_index=0
    - Move to end: source_start_index=2, source_end_index=5, destination_index=20
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return move_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_id=sheet_id,
        source_start_index=source_start_index,
        source_end_index=source_end_index,
        destination_index=destination_index
    )


@mcp.tool()
def resize_columns(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_id: int = Field(..., description="The ID of the sheet (0-based)"),
    column_indices: List[int] = Field(..., description="List of column indices to resize (0-based)"),
    widths: List[int] = Field(..., description="List of widths in pixels for each column")
) -> Dict[str, Any]:
    """
    Resize columns in a Google Sheet.
    
    Examples:
    - Resize 1 column: column_indices=[0], widths=[150]
    - Resize multiple columns: column_indices=[0, 1, 2], widths=[100, 200, 300]
    - Make columns wider: column_indices=[0, 1], widths=[200, 250]
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return resize_columns_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_id=sheet_id,
        column_indices=column_indices,
        widths=widths
    )


@mcp.tool()
def create_data_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet to create table in"),
    headers: List[str] = Field(..., description="List of header strings for the table"),
    data: List[List[str]] = Field(..., description="2D list of data rows (each row is a list of values)"),
    table_style: str = Field(default="default", description="Table style: 'default', 'striped', or 'bordered'")
) -> Dict[str, Any]:
    """
    Create a formatted data table in Google Sheets with professional styling.
    
    Features:
    - Writes headers and data to the specified sheet
    - Auto-resizes columns to fit content
    - Formats header row with bold text and dark background
    - Adds borders around the entire table
    - Center-aligns all data cells
    - Optional striped rows for better readability
    
    Examples:
    - Basic table: headers=['Name', 'Email', 'Phone'], data=[['John', 'john@email.com', '123-456-7890'], ['Jane', 'jane@email.com', '098-765-4321']]
    - Striped table: table_style='striped' for alternating row colors
    - Large dataset: data=[[...]] with many rows of data
    
    Returns table information including range, dimensions, and styling applied.
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return create_data_table(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        headers=headers,
        data=data,
        table_style=table_style
    )



if __name__ == "__main__":
    mcp.run() 