"""Google Sheets MCP Server using FastMCP - Simplified Version."""

import json
import os
from typing import Any, Dict, List, Optional, Union

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from .handler.list_spreadsheets_handler import list_all_spreadsheets_handler
from .handler.rename_spreadsheet_handler import rename_spreadsheet_handler
from .handler.list_sheets_handler import list_sheets_handler
from .handler.add_sheets_handler import add_sheets_handler
from .handler.delete_sheets_handler import delete_sheets_handler
from .handler.duplicate_sheet_handler import duplicate_sheet_handler
from .models import SheetInfo
from .handler.rename_sheets_handler import rename_sheets_handler
from .handler.read_sheet_data_handler import read_multiple_ranges
from .handler.create_chart_handler import create_chart

from .handler.get_spreadsheets_overview_handler import get_spreadsheets_overview_handler

from .handler.find_replace_handler import find_replace_text
from .handler.insert_dimension_handler import insert_dimension_handler
from .handler.delete_dimension_handler import delete_dimension
from .handler.move_dimension_handler import move_dimension
from .handler.resize_columns_handler import resize_columns_data
from .handler.format_cells_handler import format_cells_data
from .handler.conditional_format_handler import conditional_format_data
from .handler.merge_cells_handler import merge_cells_data
from .handler.add_table_handler import add_table
from .handler.delete_table_handler import delete_table
from .handler.modify_table_ranges_handler import modify_table_ranges
from .handler.add_table_records_handler import add_table_records
from .handler.get_sheet_metadata_handler import get_sheet_metadata_handler
from .handler.get_detailed_spreadsheet_metadata_handler import get_spreadsheet_metadata_handler


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
def get_all_spreadsheets_overview_tool(
    max_spreadsheets: int = Field(default=10, description="Maximum number of spreadsheets to analyze")
) -> Dict[str, Any]:
    """
    Get a comprehensive overview of all spreadsheets with their sheets.
    
    Returns a detailed overview of all accessible spreadsheets, including:
    - List of all spreadsheets with their names and IDs
    - All sheets within each spreadsheet with basic properties
    - Summary statistics across all spreadsheets
    
    This tool provides a bird's-eye view of your entire Google Sheets workspace.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return get_spreadsheets_overview_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        max_spreadsheets=max_spreadsheets
    )



@mcp.tool()
def list_all_spreadsheets(
    max_results: int = Field(default=10, description="The maximum number of spreadsheets to return")
) -> Dict[str, Any]:
    """List all spreadsheets accessible to the user.
    
    Returns a list of all Google Sheets spreadsheets that the user has access to.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return list_all_spreadsheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        max_results=max_results
    )


@mcp.tool()
def rename_spreadsheet_tool(
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet to rename"),
    new_title: str = Field(..., description="The new title for the spreadsheet")
) -> Dict[str, Any]:
    """Rename a specific spreadsheet by its name.
    
    Renames a Google Sheets spreadsheet to a new title.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return rename_spreadsheet_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        new_title=new_title
    )




@mcp.tool()
def list_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet")
) -> Dict[str, Any]:
    """List all sheets in a Google Spreadsheet.
    
    Returns basic information about all sheets in the specified spreadsheet.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return list_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name
    )


@mcp.tool()
def add_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to add as new sheets")
) -> Dict[str, Any]:
    """Add new sheets to a Google Spreadsheet.
    
    Creates new sheets with the specified names in the spreadsheet.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return add_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=sheet_names
    )


@mcp.tool()
def delete_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to delete")
) -> Dict[str, Any]:
    """Delete sheets from a Google Spreadsheet.
    
    Removes the specified sheets from the spreadsheet by their names.
    
    Examples:
    - Delete single sheet: sheet_names=["Sheet1"]
    - Delete multiple sheets: sheet_names=["Sheet1", "Data", "Temp"]
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return delete_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=sheet_names
    )


@mcp.tool()
def duplicate_sheet_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    source_sheet_name: str = Field(..., description="Name of the sheet to duplicate"),
    new_sheet_name: str = Field(default=None, description="Name for the duplicated sheet (optional, will auto-generate if not provided)"),
    insert_position: int = Field(default=None, description="Position to insert the duplicated sheet (0-based index, optional - will insert at end if not specified)")
) -> Dict[str, Any]:
    """Duplicate a sheet within a spreadsheet.
    
    Creates a copy of an existing sheet within the same spreadsheet.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return duplicate_sheet_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        source_sheet_name=source_sheet_name,
        new_sheet_name=new_sheet_name,
        insert_position=insert_position
    )


@mcp.tool()
def rename_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to rename"),
    new_titles: List[str] = Field(..., description="List of new titles for the sheets")
) -> Dict[str, Any]:
    """
    Rename sheets in a Google Spreadsheet.
    
    Renames multiple sheets by their names. The number of sheet names must match the number of new titles.
    
    Examples:
    - Rename single sheet: sheet_names=["Sheet1"], new_titles=["Summary"]
    - Rename multiple sheets: sheet_names=["Sheet1", "Data"], new_titles=["Summary", "Analysis"]
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return rename_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=sheet_names,
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
def insert_sheet_dimension(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    dimension: str = Field(..., description="Dimension to insert: 'ROWS' or 'COLUMNS'"),
    position: int = Field(..., description="Position to insert at (0-based)"),
    count: int = Field(..., description="Number of rows/columns to insert")
) -> Dict[str, Any]:
    """
    Insert rows or columns in a Google Sheet.
    
    Examples:
    - Insert 1 row: dimension="ROWS", position=5, count=1
    - Insert 3 columns: dimension="COLUMNS", position=2, count=3
    - Insert at beginning: dimension="ROWS", position=0, count=1
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return insert_dimension_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        dimension=dimension,
        position=position,
        count=count
    )


@mcp.tool()
def delete_sheet_dimension(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    dimension: str = Field(..., description="Dimension to delete: 'ROWS' or 'COLUMNS'"),
    indices: List[int] = Field(..., description="List of row/column indices to delete (0-based)")
) -> Dict[str, Any]:
    """
    Delete specific rows or columns from a Google Sheet.
    
    Examples:
    - Delete rows 5, 7, 10: dimension="ROWS", indices=[5, 7, 10]
    - Delete columns 2, 4, 6: dimension="COLUMNS", indices=[2, 4, 6]
    - Delete single row: dimension="ROWS", indices=[3]
    - Delete single column: dimension="COLUMNS", indices=[1]
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return delete_dimension(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        dimension=dimension,
        indices=indices
    )








@mcp.tool()
def move_sheet_dimension(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    dimension: str = Field(..., description="Dimension to move: 'ROWS' or 'COLUMNS'"),
    source_start_index: int = Field(..., description="Starting index to move (0-based)"),
    source_end_index: int = Field(..., description="Ending index to move (0-based, exclusive)"),
    destination_index: int = Field(..., description="Destination index (0-based)")
) -> Dict[str, Any]:
    """
    Move rows or columns in a Google Sheet.
    
    Examples:
    - Move rows 5-8 to position 10: dimension="ROWS", source_start_index=5, source_end_index=8, destination_index=10
    - Move columns 2-5 to position 0: dimension="COLUMNS", source_start_index=2, source_end_index=5, destination_index=0
    - Move single row: dimension="ROWS", source_start_index=3, source_end_index=4, destination_index=7
    - Move single column: dimension="COLUMNS", source_start_index=1, source_end_index=2, destination_index=5
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return move_dimension(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        dimension=dimension,
        source_start_index=source_start_index,
        source_end_index=source_end_index,
        destination_index=destination_index
    )


@mcp.tool()
def resize_columns(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    column_indices: List[int] = Field(..., description="List of column indices to resize (0-based)"),
    widths: List[int] = Field(..., description="List of widths in pixels for each column")
) -> Dict[str, Any]:
    """
    Resize columns in a Google Sheet.
    
    Examples:
    - Resize 1 column: sheet_name="Sheet1", column_indices=[0], widths=[150]
    - Resize multiple columns: sheet_name="Data", column_indices=[0, 1, 2], widths=[100, 200, 300]
    - Make columns wider: sheet_name="Summary", column_indices=[0, 1], widths=[200, 250]
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return resize_columns_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        column_indices=column_indices,
        widths=widths
    )





@mcp.tool()
def create_chart_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet to create chart in"),
    chart_type: str = Field(..., description="Type of chart: BAR, LINE, PIE, SCATTER, etc."),
    chart_title: str = Field(..., description="Title for the chart"),
    chart_legend: str = Field(..., description="Position of legend: TOP, BOTTOM, LEFT, RIGHT, NONE"),
    chart_position: str = Field(..., description="Position of chart on the sheet (e.g., 'A1')"),
    x_axis_label: str = Field(..., description="Label for the X-axis"),
    y_axis_label: str = Field(..., description="Label for the Y-axis"),
    x_values: List[str] = Field(..., description="List of X-axis values (e.g., ['A1:A10'])"),
    y_values: List[str] = Field(..., description="List of Y-axis values (e.g., ['B1:B10'])"),
    data_range: str = Field(..., description="Range of data to plot (e.g., 'A1:B10')")
) -> Dict[str, Any]:
    """
    Create a chart in a Google Spreadsheet.
    
    This tool allows you to create various types of charts (Bar, Line, Pie, Scatter, etc.)
    with customizable options like title, legend, position, and data ranges.
    
    Args:
        spreadsheet_name: Name of the spreadsheet to create the chart in
        sheet_name: Name of the sheet to create the chart in
        chart_type: Type of chart (e.g., 'BAR', 'LINE', 'PIE', 'SCATTER')
        chart_title: Title for the chart
        chart_legend: Position of legend (e.g., 'TOP', 'BOTTOM', 'LEFT', 'RIGHT', 'NONE')
        chart_position: Position of chart on the sheet (e.g., 'A1')
        x_axis_label: Label for the X-axis
        y_axis_label: Label for the Y-axis
        x_values: List of ranges for X-axis data (e.g., ['A1:A10'])
        y_values: List of ranges for Y-axis data (e.g., ['B1:B10'])
        data_range: Range of data to plot (e.g., 'A1:B10')
    
    Returns:
        Dict containing chart information and ID
        
    Examples:
        - Create a bar chart: chart_type='BAR', chart_title='Sales Report', chart_legend='TOP', chart_position='A1', x_axis_label='Month', y_axis_label='Sales', x_values=['A1:A12'], y_values=['B1:B12'], data_range='A1:B12'
        - Create a line chart: chart_type='LINE', chart_title='Temperature', chart_legend='NONE', chart_position='A1', x_axis_label='Date', y_axis_label='Temperature', x_values=['A1:A30'], y_values=['B1:B30'], data_range='A1:B30'
        - Create a pie chart: chart_type='PIE', chart_title='Product Sales', chart_legend='BOTTOM', chart_position='A1', x_axis_label='Product', y_axis_label='Sales', x_values=['A1:A5'], y_values=['B1:B5'], data_range='A1:B5'
    
    Note: The chart will be created in the specified sheet and position.
    """
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return create_chart(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        chart_type=chart_type,
        chart_title=chart_title,
        chart_legend=chart_legend,
        chart_position=chart_position,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        x_values=x_values,
        y_values=y_values,
        data_range=data_range
    )


@mcp.tool()
def add_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet to create table in"),
    table_name: str = Field(..., description="Unique name for the table"),
    table_range: str = Field(..., description="Table range (e.g., 'A1:C10'). The actual table will include all columns based on the number of headers, regardless of the range end column."),
    headers: List[str] = Field(..., description="List of column headers"),
    data: List[List[str]] = Field(default=[], description="2D list of data rows (optional)"),
    column_types: List[str] = Field(default=None, description="Column types: DOUBLE, CURRENCY, DATE, TEXT, etc. (optional)")
) -> Dict[str, Any]:
    """
    Create a native Google Sheets table using AddTableRequest.
    
    This creates a proper table object with:
    - Table ID and name for future reference
    - Column properties and data types
    - Professional styling with header and alternating row colors
    - Data validation capabilities
    
    Supported column types:
    - TEXT/STRING: Text columns (no validation applied)
    - NUMBER/DOUBLE/INTEGER/CURRENCY: Number columns with positive number validation
    - DATE: Date columns with date validation (after 1900)
    - BOOLEAN: Boolean columns (no validation applied)
    
    Examples:
    - Basic table: table_name='SalesData', table_range='A1:C10', headers=['Name', 'Amount', 'Date']
    - Typed columns: column_types=['TEXT', 'CURRENCY', 'DATE']
    - Dropdown column: column_types=['TEXT', 'DROPDOWN', 'DATE']
    
    Returns table information including table ID for future operations.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return add_table(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        table_range=table_range,
        headers=headers,
        data=data,
        column_types=column_types
    )


@mcp.tool()
def delete_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to delete")
) -> Dict[str, Any]:
    """
    Delete a native Google Sheets table using DeleteTableRequest.
    
    This tool completely removes the table object and all its data from the sheet.
    The table structure, formatting, validation rules, and data will be permanently deleted.
    
    ⚠️ WARNING: This action is irreversible. All table data will be lost.
    
    Args:
        spreadsheet_name: Name of the spreadsheet containing the table
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete
    
    Returns:
        Dict containing deletion results with table information
        
    Examples:
        - Delete a table: table_name="SalesData"
        - Remove unwanted table: table_name="OldInventory"
    
    Note: The table will be found by name, so you don't need to know the table ID.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return delete_table(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name
    )




@mcp.tool()
def add_table_records_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to add records to"),
    data: List[List[Union[str, int, float, bool]]] = Field(..., description="2D list of data rows to add (supports strings, numbers, booleans)"),
    operation: str = Field(default="APPEND", description="Operation type: APPEND or INSERT"),
    position: int = Field(default=None, description="Position to insert data (0-based, required for INSERT operation)"),
    append_position: str = Field(default="END", description="Where to append: START or END (for APPEND operation)")
) -> Dict[str, Any]:
    """
    Add records to a native Google Sheets table.
    
    This tool can either:
    - APPEND: Add new data rows to the end/start of an existing table
    - INSERT: Insert new data rows at a specific position within the table
    
    The tool automatically detects data types:
    - Numbers (int/float) → numberValue
    - Booleans → boolValue  
    - Strings → stringValue
    
    Args:
        spreadsheet_name: Name of the spreadsheet containing the table
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add records to
        data: 2D list of data rows to add (supports mixed types)
        operation: Operation type ("APPEND" or "INSERT")
        position: Position to insert data (0-based, required for INSERT)
        append_position: Where to append (START or END, for APPEND operation)
    
    Returns:
        Dict containing operation results with table information
        
    Examples:
        # Append to end (default)
        - Mixed data types: data=[["John", 100, True], ["Jane", 200.5, False]]
        - String data: data=[["Product A", "Category 1"], ["Product B", "Category 2"]]
        - Append to start: operation="APPEND", append_position="START"
        
        # Insert at specific position
        - Insert at position 2: operation="INSERT", position=2, data=[["New Row", 150]]
        - Insert at position 0: operation="INSERT", position=0, data=[["First Row", 50]]
        - Insert multiple rows: operation="INSERT", position=3, data=[["Row 1", 100], ["Row 2", 200]]
    
    Note: The table will be found by name, so you don't need to know the table ID.
    Data types are automatically detected and preserved in the table.
    For INSERT operations, existing data is shifted down to make room for new rows.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return add_table_records(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        data=data,
        operation=operation,
        position=position,
        append_position=append_position
    )


@mcp.tool()
def modify_table_ranges_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to modify ranges in"),
    operation: str = Field(..., description="Operation to perform: INSERT or DELETE"),
    range_to_modify: str = Field(..., description="Range to modify (e.g., 'A1:C5')"),
    shift_direction: str = Field(default="ROWS", description="Shift direction: ROWS or COLUMNS"),
    data: Optional[List[List[Union[str, int, float, bool]]]] = Field(default=None, description="Data to insert (for INSERT operations)")
) -> Dict[str, Any]:
    """
    Modify ranges within a native Google Sheets table using InsertRangeRequest/DeleteRangeRequest.
    
    This unified tool can either insert or delete ranges of cells and shift existing data accordingly.
    It's more precise than dimension-based operations as it works with specific ranges.
    
    Args:
        spreadsheet_name: Name of the spreadsheet containing the table
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to modify ranges in
        operation: Operation to perform ("INSERT" or "DELETE")
        range_to_modify: Range to modify (e.g., 'A1:C5')
        shift_direction: Shift direction ("ROWS" or "COLUMNS")
        data: Optional data to insert (for INSERT operations)
    
    Returns:
        Dict containing operation results with table information
        
    Examples:
        - Insert range A1:C5: operation="INSERT", range_to_modify="A1:C5", shift_direction="ROWS"
        - Delete range B2:D4: operation="DELETE", range_to_modify="B2:D4", shift_direction="COLUMNS"
        - Insert range with data: operation="INSERT", range_to_modify="A1:C3", data=[["John", 100], ["Jane", 200]]
        - Delete single cell: operation="DELETE", range_to_modify="A1:A1", shift_direction="ROWS"
    
    Note: The table will be found by name, so you don't need to know the table ID.
    For INSERT operations, the range will be empty unless data is provided.
    For DELETE operations, the range will be removed and remaining data will be shifted.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return modify_table_ranges(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        operation=operation,
        range_to_modify=range_to_modify,
        shift_direction=shift_direction,
        data=data
    )


@mcp.tool()
def get_sheet_metadata_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the specific sheet to get detailed metadata for")
) -> str:
    """
    Get comprehensive metadata about a specific sheet including grid data, formatting, properties, charts, tables, slicers, and drawings.
    
    This tool provides detailed information about a single sheet structure, including:
    - Grid properties (row/column counts, frozen panes, gridlines)
    - Row and column metadata (heights, widths, hidden status)
    - Data statistics (rows with data, total cells, non-empty cells)
    - Merged cells information
    - Basic filters and sorting
    - Charts with detailed specifications (chart types, data ranges, axis labels, legends)
    - Tables with range and properties information
    - Slicers for interactive filtering
    - Drawings and visual elements
    - Conditional formatting and protected ranges
    - Developer metadata and custom structures
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the specific sheet to get metadata for (required)
    
    Returns:
        Compact JSON string containing comprehensive metadata for the specified sheet
        
    Examples:
        # Get detailed metadata for a specific sheet
        - spreadsheet_name="My Spreadsheet", sheet_name="Sheet1"
        
    Note: This tool provides the most comprehensive metadata available for a single sheet
    including charts, tables, slicers, and drawings.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return get_sheet_metadata_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name
    )


@mcp.tool()
def get_spreadsheet_metadata_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet")
) -> str:
    """
    Get metadata about a spreadsheet including basic information about sheets, named ranges, and developer metadata.
    
    This tool provides basic information about the spreadsheet structure, including:
    - Spreadsheet-level properties (title, locale, timeZone, defaultCellFormat)
    - Basic sheet information (names, counts, hidden status)
    - Named ranges and developer metadata
    - Summary statistics
    
    Args:
        spreadsheet_name: Name of the spreadsheet to analyze
    
    Returns:
        Dict containing basic spreadsheet metadata
        
    Examples:
        # Get metadata for a spreadsheet
        - spreadsheet_name="My Spreadsheet"
        
    Note: This tool provides basic metadata about the spreadsheet structure.
    It excludes grid cell data to focus on structure and metadata only.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return get_spreadsheet_metadata_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name
    )


if __name__ == "__main__":
    mcp.run() 