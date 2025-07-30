"""Google Sheets MCP Server using FastMCP - Simplified Version."""

# Standard library imports
import json
import os
from typing import Any, Dict, List, Optional, Union

# Third-party library imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Local imports - Models
from .models import SheetInfo

# Local imports - Spreadsheet management handlers
from .handler.list_spreadsheets_handler import list_all_spreadsheets_handler
from .handler.rename_spreadsheet_handler import rename_spreadsheet_handler
from .handler.get_spreadsheets_overview_handler import get_spreadsheets_overview_handler

# Local imports - Sheet management handlers
from .handler.list_sheets_handler import list_sheets_handler
from .handler.add_sheets_handler import add_sheets_handler
from .handler.delete_sheets_handler import delete_sheets_handler
from .handler.duplicate_sheet_handler import duplicate_sheet_handler
from .handler.rename_sheets_handler import rename_sheets_handler
from .handler.get_sheet_metadata_handler import get_sheet_metadata_handler
from .handler.get_detailed_spreadsheet_metadata_handler import get_spreadsheet_metadata_handler

# Local imports - Data reading handlers
from .handler.read_sheet_data_handler import read_multiple_ranges, read_sheet_data_handler

# Local imports - Content manipulation handlers
from .handler.find_replace_handler import find_replace_text
from .handler.insert_dimension_handler import insert_dimension_handler
from .handler.delete_dimension_handler import delete_dimension
from .handler.move_dimension_handler import move_dimension
from .handler.resize_columns_handler import resize_columns_data

# Local imports - Formatting handlers
from .handler.format_cells_handler import format_cells_data
from .handler.conditional_format_handler import conditional_format_data
from .handler.merge_cells_handler import merge_cells_data

# Local imports - Chart creation handlers
from .handler.create_chart_handler import create_chart

# Local imports - Table management handlers
from .handler.add_table_handler import add_table
from .handler.delete_table_handler import delete_table
from .handler.get_table_metadata_handler import get_table_metadata
from .handler.add_table_records_handler import add_table_records
from .handler.delete_table_records_handler import delete_table_records
from .handler.add_table_column_handler import add_table_column
from .handler.delete_table_column_handler import delete_table_column


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


# =============================================================================
# SPREADSHEET RELATED TOOLS
# =============================================================================

@mcp.tool()
def get_all_spreadsheets_overview_tool(
    max_spreadsheets: int = Field(default=10, description="Maximum number of spreadsheets to analyze")
) -> str:
    """
    Get a comprehensive overview of all spreadsheets with their sheets.
    Returns compact JSON string for AI host compatibility.

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
) -> str:
    """List all spreadsheets accessible to the user.
    
    Returns a list of all Google Sheets spreadsheets that the user has access to.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """
    Rename a Google Spreadsheet.
    Returns compact JSON string for AI host compatibility.
    
    This tool changes the title/name of an existing spreadsheet.
    
    Examples:
    - Rename spreadsheet: spreadsheet_name="Old Name", new_title="New Name"
    - Update title: spreadsheet_name="Data 2023", new_title="Data 2024"
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


# =============================================================================
# SHEETS RELATED TOOLS
# =============================================================================

@mcp.tool()
def list_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet")
) -> str:
    """List all sheets in a Google Spreadsheet.
    
    Returns basic information about all sheets in the specified spreadsheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Add new sheets to a Google Spreadsheet.
    
    Creates new sheets with the specified names in the spreadsheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Delete sheets from a Google Spreadsheet.
    
    Removes the specified sheets from the spreadsheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Duplicate a sheet in a Google Spreadsheet.
    
    Creates a copy of the specified sheet with all its content and formatting.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Rename sheets in a Google Spreadsheet.
    
    Changes the names of specified sheets in the spreadsheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Read data from multiple ranges in a Google Spreadsheet.
    
    Retrieves data from specified ranges in the spreadsheet.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return read_sheet_data_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        ranges=ranges,
        value_render_option=value_render_option,
        date_time_render_option=date_time_render_option
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
def find_replace(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    search_range: str = Field(..., description="Range to search in (e.g., 'Sheet1!A:A', 'Sheet1!A1:Z100')"),
    find_text: str = Field(..., description="Text to find"),
    replace_text: str = Field(..., description="Text to replace with"),
    match_case: bool = Field(default=False, description="Whether to match case (default: False)")
) -> str:
    """Find and replace text in a Google Spreadsheet.
    
    Searches for specified text in the given range and replaces it with new text.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return find_replace_text(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        search_range=search_range,
        find_text=find_text,
        replace_text=replace_text,
        match_case=match_case
    )


@mcp.tool()
def insert_sheet_dimension(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    dimension: str = Field(..., description="Dimension to insert: 'ROWS' or 'COLUMNS'"),
    position: int = Field(..., description="Position to insert at (0-based)"),
    count: int = Field(..., description="Number of rows/columns to insert")
) -> str:
    """Insert rows or columns in a Google Spreadsheet.
    
    Adds new rows or columns at the specified position in the sheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Delete rows or columns from a Google Spreadsheet.
    
    Removes specified rows or columns from the sheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Move rows or columns in a Google Spreadsheet.
    
    Relocates specified rows or columns to a new position in the sheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Resize columns in a Google Spreadsheet.
    
    Changes the width of specified columns in the sheet.
    Returns compact JSON string for AI host compatibility.
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
def format_cells(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    range_name: str = Field(..., description="Range to format (e.g., 'A1:B10')"),
    format_type: str = Field(..., description="Type of formatting: 'TEXT', 'NUMBER', 'PERCENT', 'CURRENCY', 'DATE', 'TIME', 'DATETIME'"),
    format_pattern: str = Field(default=None, description="Custom format pattern (optional)")
) -> str:
    """Format cells in a Google Spreadsheet.
    
    Applies specified formatting to cells in the given range.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return format_cells_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        range_name=range_name,
        format_type=format_type,
        format_pattern=format_pattern
    )


@mcp.tool()
def conditional_format(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    range_name: str = Field(..., description="Range to apply conditional formatting to (e.g., 'A1:B10')"),
    condition_type: str = Field(..., description="Type of condition: 'NUMBER_GREATER', 'NUMBER_LESS', 'TEXT_CONTAINS', 'DATE_BEFORE', 'DATE_AFTER'"),
    condition_value: str = Field(..., description="Value to compare against"),
    format_color: str = Field(default="RED", description="Color for the format (e.g., 'RED', 'GREEN', 'BLUE')")
) -> str:
    """Apply conditional formatting to cells in a Google Spreadsheet.
    
    Sets up conditional formatting rules for the specified range.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return conditional_format_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        range_name=range_name,
        condition_type=condition_type,
        condition_value=condition_value,
        format_color=format_color
    )


@mcp.tool()
def merge_cells(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    range_name: str = Field(..., description="Range to merge (e.g., 'A1:B2')"),
    merge_type: str = Field(default="MERGE_ALL", description="Type of merge: 'MERGE_ALL', 'MERGE_COLUMNS', 'MERGE_ROWS'")
) -> str:
    """Merge cells in a Google Spreadsheet.
    
    Combines cells in the specified range according to the merge type.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return merge_cells_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        range_name=range_name,
        merge_type=merge_type
    )


# =============================================================================
# TABLES RELATED TOOLS
# =============================================================================

@mcp.tool()
def add_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet to create table in"),
    table_name: str = Field(..., description="Unique name for the table"),
    table_range: str = Field(..., description="Table range (e.g., 'A1:C10'). The actual table will include all columns based on the number of headers, regardless of the range end column."),
    headers: List[str] = Field(..., description="List of column headers"),
    data: List[List[str]] = Field(default=[], description="2D list of data rows (optional)"),
    column_types: List[str] = Field(default=None, description="Column types: DOUBLE, CURRENCY, DATE, TEXT, etc. (optional)")
) -> str:
    """Create a table in a Google Spreadsheet.
    
    Creates a structured table with headers and optional data in the sheet.
    Returns compact JSON string for AI host compatibility.
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
) -> str:
    """Delete a table from a Google Spreadsheet.
    
    Removes the specified table from the sheet.
    Returns compact JSON string for AI host compatibility.
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
def get_table_metadata_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to get metadata for")
) -> str:
    """Get metadata about a table in a Google Spreadsheet.
    
    Retrieves detailed information about the specified table.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return get_table_metadata(
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
) -> str:
    """Add records to a table in a Google Spreadsheet.
    
    Inserts new data rows into the specified table.
    Returns compact JSON string for AI host compatibility.
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
def delete_table_records_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to delete records from"),
    row_indices: List[int] = Field(..., description="List of row indices to delete (0-based, relative to table data rows, excluding header)"),
    delete_type: str = Field(default="ROWS", description="Type of deletion: ROWS (delete entire rows) or CLEAR (clear cell contents only)")
) -> str:
    """Delete records from a table in a Google Spreadsheet.
    
    Removes specified data rows from the table.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return delete_table_records(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        row_indices=row_indices,
        delete_type=delete_type
    )


@mcp.tool()
def add_table_column_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to add column to"),
    column_name: str = Field(..., description="Name/header for the new column"),
    column_type: str = Field(default="TEXT", description="Column type: TEXT, DOUBLE, CURRENCY, DATE, etc."),
    position: Optional[int] = Field(default=None, description="Position to insert column (0-based, optional - adds at end if not specified)"),
    data: List[str] = Field(default=[], description="List of data values for the new column (optional)")
) -> str:
    """Add a column to a table in a Google Spreadsheet.
    
    Creates a new column in the specified table.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return add_table_column(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        column_name=column_name,
        column_type=column_type,
        position=position,
        data=data
    )


@mcp.tool()
def delete_table_column_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to delete column from"),
    column_index: int = Field(..., description="Index of the column to delete (0-based)")
) -> str:
    """Delete a column from a table in a Google Spreadsheet.
    
    Removes the specified column from the table.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return delete_table_column(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        column_index=column_index
    )


# =============================================================================
# CHARTS RELATED TOOLS
# =============================================================================

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
) -> str:
    """Create a chart in a Google Spreadsheet.
    
    Generates a chart with the specified type and data in the sheet.
    Returns compact JSON string for AI host compatibility.
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
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


# =============================================================================
# OTHERS
# =============================================================================

# No additional tools in this category currently


if __name__ == "__main__":
    mcp.run() 