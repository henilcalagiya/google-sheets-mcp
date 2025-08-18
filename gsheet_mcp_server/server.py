"""Google Sheets MCP Server using FastMCP - Environment Variables Version."""

# Standard library imports
import json
import os
from typing import Dict, List, Optional, Union, Any

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
from .handler.spreadsheet.update_spreadsheet_title_handler import update_spreadsheet_title_handler
from .handler.spreadsheet.discover_spreadsheets_handler import discover_spreadsheets_handler

# Local imports - Sheets handlers
from .handler.sheets.create_sheets_handler import create_sheets_handler
from .handler.sheets.delete_sheets_handler import delete_sheets_handler
from .handler.sheets.create_duplicate_sheet_handler import create_duplicate_sheet_handler
from .handler.sheets.update_sheet_titles_handler import update_sheet_titles_handler
from .handler.sheets.analyze_sheet_structure_handler import analyze_sheet_structure_handler

# Local imports - Table management handlers
from .handler.tables.create_table_handler import create_table_handler
from .handler.tables.delete_table_handler import delete_table_handler
from .handler.tables.update_table_title_handler import update_table_title_handler
from .handler.tables.get_table_metadata_handler import get_table_metadata_handler
from .handler.tables.add_table_column_handler import add_table_column_handler


from .handler.tables.update_table_sorting_handler import update_table_sorting_handler

from .handler.tables.delete_table_records_handler import delete_table_records_handler


from .handler.tables.update_table_cells_by_notation_handler import update_table_cells_by_notation_handler
from .handler.tables.get_sheet_cells_by_notation_handler import get_sheet_cells_by_notation_handler
from .handler.tables.update_table_column_name_handler import update_table_column_name_handler
from .handler.tables.update_table_column_type_handler import update_table_column_type_handler




from .handler.tables.get_table_data_handler import get_table_data_handler
from .handler.tables.update_dropdown_options_handler import update_dropdown_options_handler
from .handler.tables.delete_table_column_handler import delete_table_column_handler
from .handler.tables.get_sheet_cells_by_range_handler import get_sheet_cells_by_range_handler
from .handler.tables.update_table_cells_by_range_handler import update_table_cells_by_range_handler

from .handler.tables.add_table_records_handler import add_table_records_handler

# Create an MCP server
mcp = FastMCP("Google Sheets MCP")

# Global variables for services (will be initialized lazily)
_sheets_service = None
_drive_service = None

def _get_google_services():
    """Get or initialize Google services lazily."""
    global _sheets_service, _drive_service
    
    if _sheets_service is None or _drive_service is None:
        _sheets_service, _drive_service = _setup_google_services_from_env()
    
    return _sheets_service, _drive_service

def _setup_google_services_from_env():
    """Set up Google Sheets and Drive API services from environment variables."""
    try:
        # Get all credential components from environment variables
        # Support both GOOGLE_ prefixed and direct Google JSON field names
        project_id = os.getenv("project_id") or os.getenv("GOOGLE_PROJECT_ID")
        private_key_id = os.getenv("private_key_id") or os.getenv("GOOGLE_PRIVATE_KEY_ID")
        private_key = os.getenv("private_key") or os.getenv("GOOGLE_PRIVATE_KEY")
        client_email = os.getenv("client_email") or os.getenv("GOOGLE_CLIENT_EMAIL")
        client_id = os.getenv("client_id") or os.getenv("GOOGLE_CLIENT_ID")
        auth_uri = os.getenv("auth_uri") or os.getenv("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
        token_uri = os.getenv("token_uri") or os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token")
        auth_provider_x509_cert_url = os.getenv("auth_provider_x509_cert_url") or os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
        client_x509_cert_url = os.getenv("client_x509_cert_url") or os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
        
        # Validate required fields
        required_fields = {
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "client_id": client_id,
            "client_x509_cert_url": client_x509_cert_url
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
        
        # Construct service account info
        service_account_info = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key.replace('\\n', '\n'),  # Handle escaped newlines
            "client_email": client_email,
            "client_id": client_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
            "client_x509_cert_url": client_x509_cert_url
        }
        
        # Create credentials
        credentials = ServiceAccountCredentials.from_service_account_info(
            service_account_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly",
            ],
        )
        
        # Build the services
        sheets_service = build("sheets", "v4", credentials=credentials)
        drive_service = build("drive", "v3", credentials=credentials)
        return sheets_service, drive_service
        
    except Exception as e:
        raise RuntimeError(f"Failed to setup Google services from environment variables: {str(e)}")

@mcp.tool()
def discover_spreadsheets_tool(
    max_spreadsheets: int = Field(default=10, description="Maximum number of spreadsheets to analyze")
) -> str:
    """
    Discover spreadsheets and their sheet names.
    
    Args:
        max_spreadsheets: Maximum number of spreadsheets to analyze (default: 10)
    
    Returns:
        JSON string containing spreadsheet names and their sheet names
    """
    sheets_service, drive_service = _get_google_services()
    return discover_spreadsheets_handler(
        drive_service, sheets_service, max_spreadsheets
    )


@mcp.tool()
def update_spreadsheet_title_tool(
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet to rename"),
    new_title: str = Field(..., description="The new title for the spreadsheet")
) -> str:
    """
    Update a Google Spreadsheet title.
    """
    sheets_service, drive_service = _get_google_services()
    return update_spreadsheet_title_handler(drive_service, sheets_service, spreadsheet_name, new_title)


@mcp.tool()
def create_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to create as new sheets")
) -> str:
    """
    Create new sheets in a Google Spreadsheet.
    """
    sheets_service, drive_service = _get_google_services()
    return create_sheets_handler(drive_service, sheets_service, spreadsheet_name, sheet_names)


@mcp.tool()
def delete_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to delete")
) -> str:
    """
    Delete sheets from a Google Spreadsheet.
    """
    sheets_service, drive_service = _get_google_services()
    return delete_sheets_handler(drive_service, sheets_service, spreadsheet_name, sheet_names)


@mcp.tool()
def create_duplicate_sheet_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    source_sheet_name: str = Field(..., description="Name of the sheet to duplicate"),
    new_sheet_name: str = Field(default="", description="Name for the duplicated sheet (optional, will auto-generate if not provided)"),
    insert_position: int = Field(default=None, description="Position to insert the duplicated sheet (1-based index, optional - will insert at end if not specified)")
) -> str:
    """
    Create a duplicate of an existing sheet.
    """
    sheets_service, drive_service = _get_google_services()
    return create_duplicate_sheet_handler(drive_service, sheets_service, spreadsheet_name, source_sheet_name, new_sheet_name, insert_position)


@mcp.tool()
def update_sheet_titles_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to rename (put only the names of the sheets you want to rename)"),
    new_titles: List[str] = Field(..., description="List of new titles for the sheets")
) -> str:
    """
    Update sheet titles in a Google Spreadsheet.
    """
    sheets_service, drive_service = _get_google_services()
    return update_sheet_titles_handler(drive_service, sheets_service, spreadsheet_name, sheet_names, new_titles)


@mcp.tool()
def analyze_sheet_structure_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the specific sheet to analyze")
) -> str:
    """
    Analyze a specific sheet's structure - quick overview.
    
    This tool provides a simple overview of what's in the sheet:
    - Sheet basic info (name, size, hidden status)
    - Tables (count, names, ranges, sizes)
    - Charts (count, IDs, positions)
    - Slicers (count, IDs, positions)
    - Drawings (count, IDs, positions)
    - Developer metadata (count, keys, values)
    - Summary (total elements, sheet type, frozen panes)
    
    Args:
        spreadsheet_name: The name of the Google Spreadsheet
        sheet_name: Name of the specific sheet to analyze
    
    Returns:
        JSON string with simplified structure overview
    """
    sheets_service, drive_service = _get_google_services()
    return analyze_sheet_structure_handler(drive_service, sheets_service, spreadsheet_name, sheet_name)


@mcp.tool()
def create_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet to create table in"),
    table_name: str = Field(..., description="A descriptive name for the table (e.g., 'Project Tracker', 'Customer Data')"),
    start_cell: str = Field(..., description="Starting cell for the table (e.g., 'A1')"),
    column_names: List[str] = Field(..., description="List of column names (e.g., ['Employee Name', 'Age', 'Department', 'Salary'])"),
    column_types: List[str] = Field(..., description="List of column types:  DOUBLE, CURRENCY, PERCENT, DATE, TIME, DATE_TIME, TEXT, BOOLEAN, DROPDOWN"),
    dropdown_columns: List[str] = Field(default=[], description="List of column names that should have dropdown validation"),
    dropdown_values: List[str] = Field(default=[], description="Comma-separated dropdown options for each dropdown column")
) -> str:
    """
    Create a new table in Google Sheets.
    
    This tool creates a structured table with specified columns and data types.
    Tables provide better data organization, validation, and formatting capabilities.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to create table in
        table_name: Name for the table
        start_cell: Starting cell for the table (e.g., "A1")
        column_names: List of column names
        column_types: List of column types corresponding to column_names
        dropdown_columns: List of column names that should have dropdown validation
        dropdown_values: List of comma-separated dropdown options for each dropdown column
    
    Returns:
        JSON string with success status and table details
    """
    sheets_service, drive_service = _get_google_services()
    return create_table_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, start_cell, column_names, column_types, dropdown_columns, dropdown_values)


@mcp.tool()
def delete_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the tables"),
    table_names: List[str] = Field(..., description="List of table names to delete (e.g., ['Project Tracker', 'Customer Data', 'Sales Report'])")
) -> str:
    """
    Delete tables from Google Sheets.
    
    This tool removes specified tables from a sheet while preserving other content.
    The table structure and data will be permanently deleted.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the tables
        table_names: List of table names to delete
    
    Returns:
        JSON string with success status and deletion details
    """
    sheets_service, drive_service = _get_google_services()
    return delete_table_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_names)


@mcp.tool()
def update_table_title_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    old_table_name: str = Field(..., description="Current name of the table to update"),
    new_table_name: str = Field(..., description="New title for the table")
) -> str:
    """
    Update a table title in Google Sheets.
    
    This tool allows you to update the title of an existing table.
    The table structure and data remain unchanged.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        old_table_name: Current name of the table to update
        new_table_name: New title for the table
    
    Returns:
        JSON string with success status and update details
    """
    sheets_service, drive_service = _get_google_services()
    return update_table_title_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, old_table_name, new_table_name)


@mcp.tool()
def get_table_metadata_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(default=None, description="Name of the table to get metadata for. If not provided, returns metadata for all tables in the sheet."),
    include_sample_data: bool = Field(default=False, description="Whether to include sample data rows"),
    include_formulas: bool = Field(default=False, description="Whether to include formula information"),
    include_formatting: bool = Field(default=False, description="Whether to include cell formatting details"),
    include_statistics: bool = Field(default=False, description="Whether to include data statistics"),
    max_sample_rows: int = Field(default=5, description="Maximum number of sample rows to return"),
    specific_columns: List[str] = Field(default=None, description="List of column names to get metadata for (optional)"),
    exclude_metadata_types: List[str] = Field(default=None, description="List of metadata types to exclude (e.g., ['sample_data', 'formatting', 'statistics', 'merges', 'conditional_formatting', 'filters'])")
) -> str:
    """
    Get comprehensive metadata for tables in Google Sheets.
    
    This tool provides detailed information about table structure, columns, data types,
    formatting, statistics, and other properties. If no table name is provided, returns 
    metadata for all tables.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to get metadata for (optional)
        include_sample_data: Whether to include sample data rows
        include_formulas: Whether to include formula information
        include_formatting: Whether to include cell formatting details
        include_statistics: Whether to include data statistics
        max_sample_rows: Maximum number of sample rows to return
        specific_columns: List of column names to get metadata for (optional)
        exclude_metadata_types: List of metadata types to exclude
    
    Returns:
        JSON string containing table metadata or list of all tables
    """
    sheets_service, drive_service = _get_google_services()
    return get_table_metadata_handler(
        drive_service,
        sheets_service,
        spreadsheet_name,
        sheet_name,
        table_name,
        include_sample_data,
        include_formulas,
        include_formatting,
        include_statistics,
        max_sample_rows,
        specific_columns,
        exclude_metadata_types
    )


@mcp.tool()
def add_table_column_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to add columns to"),
    column_names: List[str] = Field(..., description="List of column names (e.g., ['Status', 'Priority', 'Notes'])"),
    column_types: List[str] = Field(..., description="List of column types: DOUBLE, CURRENCY, PERCENT, DATE, TIME, DATE_TIME, TEXT, BOOLEAN, DROPDOWN"),
    positions: List[int] = Field(default=[], description="List of positions to insert columns (0-based index, empty list for end)"),
    dropdown_columns: List[str] = Field(default=[], description="List of column names that should have dropdown validation"),
    dropdown_values: List[str] = Field(default=[], description="Comma-separated dropdown options for each dropdown column")
) -> str:
    """
    Add new columns to an existing table in Google Sheets.
    
    This tool extends an existing table with additional columns.
    New columns can have different data types and validation rules.
    Supports adding multiple columns at once with proper positioning.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add columns to
        column_names: List of column names to add
        column_types: List of column types corresponding to column_names
        positions: List of positions to insert columns (0-based index, empty list for end)
        dropdown_columns: List of column names that should have dropdown validation
        dropdown_values: List of comma-separated dropdown options for each dropdown column
    
    Returns:
        JSON string with success status and column addition details
    """
    sheets_service, drive_service = _get_google_services()
    return add_table_column_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_names, column_types, positions, dropdown_columns, dropdown_values)


@mcp.tool()
def update_table_sorting_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to sort"),
    column_name: str = Field(..., description="Name of the column to sort by"),
    sort_order: str = Field(default="ASC", description="Sort order: 'ASC' or 'DESC' (default: 'ASC')")
) -> str:
    """
    Update table sorting by a specific column.
    
    This tool sorts all data rows in a table based on a specified column.
    The header row remains in place, and data rows are reordered.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to sort
        column_name: Name of the column to sort by
        sort_order: Sort order - "ASC" or "DESC" (default: "ASC")
    
    Returns:
        JSON string with success status and sorting details
    """
    sheets_service, drive_service = _get_google_services()
    return update_table_sorting_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_name, sort_order)


@mcp.tool()
def delete_table_records_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to delete records from"),
    record_numbers: List[int] = Field(..., description="List of record numbers to delete (1-based, excluding header)")
) -> str:
    """
    Delete specific records (rows) from a table.
    
    This tool removes specific records from a table while preserving the table structure.
    Record numbers are 1-based and exclude the header row. Records are deleted in descending order
    (bigger numbers first) to avoid index shifting issues.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete records from
        record_numbers: List of record numbers to delete (1-based, excluding header)
    
    Returns:
        JSON string with success status and deletion details
    """
    sheets_service, drive_service = _get_google_services()
    return delete_table_records_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, record_numbers)


@mcp.tool()
def update_table_cells_by_notation_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to update"),
    cell_updates: List[Dict[str, Union[str, int, float, bool, None]]] = Field(..., description="""List of cell updates, each containing:
    - cell_notation: Cell reference in A1 notation (e.g., 'A1', 'B5')
    - value: New value for the cell (string, number, boolean, or None)
    
    EXAMPLE: [
        {"cell_notation": "A1", "value": "New Value"},
        {"cell_notation": "B5", "value": 50000},
        {"cell_notation": "C10", "value": True}
    ]
    """)
) -> str:
    """
    Update specific cells in a table.
    
    This tool updates multiple cells in a table with new values using A1 notation.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        cell_updates: List of cell updates with cell_notation and value
    
    Returns:
        JSON string with success status and update details
    """
    sheets_service, drive_service = _get_google_services()
    return update_table_cells_by_notation_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, cell_updates)


@mcp.tool()
def get_sheet_cells_by_notation_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet to get cells from"),
    cell_notations: List[str] = Field(..., description="List of cell notations to get values from (e.g., ['A1', 'A6', 'A10', 'E5'])")
) -> str:
    """
    Get values from specific cells in a sheet.
    
    This tool retrieves values from multiple cells in a sheet using A1 notation.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to get cells from
        cell_notations: List of cell notations to get values from (e.g., ['A1', 'A6', 'A10', 'E5'])
    
    Returns:
        JSON string with cell values and mapping
    """
    sheets_service, drive_service = _get_google_services()
    return get_sheet_cells_by_notation_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, cell_notations)


@mcp.tool()
def update_table_column_name_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to update column names in"),
    column_indices: List[int] = Field(..., description="List of column indices to update (0-based)"),
    new_column_names: List[str] = Field(..., description="List of new column names (must match column_indices count)")
) -> str:
    """
    Update column names in a table.
    
    This tool updates existing column names in a table by their index.
    The number of column indices must match the number of new column names.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update column names in
        column_indices: List of column indices to update (0-based)
        new_column_names: List of new column names
    
    Returns:
        JSON string with success status and update details
    """
    sheets_service, drive_service = _get_google_services()
    return update_table_column_name_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_indices, new_column_names)


@mcp.tool()
def update_table_column_type_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to update column types in"),
    column_names: List[str] = Field(..., description="List of column names to update types for"),
    new_column_types: List[str] = Field(..., description="List of new column types (must match column_names count)")
) -> str:
    """
    Update column types in a table.
    
    This tool updates the data type of existing columns in a table.
    The number of column names must match the number of new column types.
    
    Available column types:
    - DOUBLE: Numeric data with decimals
    - CURRENCY: Monetary values ($#,##0.00)
    - PERCENT: Percentage values (0.00%)
    - DATE: Date values (yyyy-mm-dd)
    - TIME: Time values (hh:mm:ss)
    - DATE_TIME: Date and time values
    - TEXT: Plain text data
    - BOOLEAN: True/false values
    - DROPDOWN: Selection from predefined options
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update column types in
        column_names: List of column names to update types for
        new_column_types: List of new column types
    
    Returns:
        JSON string with success status and type update details
    """
    sheets_service, drive_service = _get_google_services()
    return update_table_column_type_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_names, new_column_types)


@mcp.tool()
def get_table_data_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to read data from"),
    column_names: List[str]  = Field(default=[], description="List of column names to retrieve (optional - if not provided, gets all columns)"),
    start_row: int = Field(default=-1, description="Starting row index (0-based, optional, use -1 for all rows)"),
    end_row: int = Field(default=-1, description="Ending row index (0-based, optional, use -1 for all rows)"),
    include_headers: bool = Field(default=True, description="Whether to include header row in results"),
    max_rows: int = Field(default=-1, description="Maximum number of rows to return (optional, use -1 for no limit)")
) -> str:
    """
    Get table data with optional column filtering using Google Sheets API.
    
    This unified tool can retrieve all table data or specific columns based on user input.
    If column_names is provided, it uses spreadsheets.values.get for efficiency.
    If column_names is not provided, it uses spreadsheets.tables.get for full data.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to read data from
        column_names: List of column names to retrieve (optional - if not provided, gets all columns)
        start_row: Starting row index (0-based, optional)
        end_row: Ending row index (0-based, optional)
        include_headers: Whether to include header row in results
        max_rows: Maximum number of rows to return (optional)
    
    Returns:
        JSON string with table data and metadata
    """
    sheets_service, drive_service = _get_google_services()
    return get_table_data_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_names, start_row, end_row, include_headers, max_rows)


@mcp.tool()
def update_dropdown_options_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to update dropdown options in"),
    action: str = Field(..., description="Action to perform: 'add' or 'remove'"),
    column_name: str = Field(..., description="Name of the column to update dropdown options for"),
    dropdown_options: List[str] = Field(default=[], description="List of dropdown options to add/remove (required for 'add' and 'remove' actions)")
) -> str:
    """
    Update dropdown options in a table column.
    
    This tool can add or remove specific dropdown options from an existing column in a table.
    For 'add' action: Adds new options to existing dropdown (preserves existing options).
    For 'remove' action: Removes specific options from existing dropdown.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update dropdown options in
        action: Action to perform - "add" or "remove"
        column_name: Name of the column to update dropdown options for
        dropdown_options: List of dropdown options to add/remove
    
    Returns:
        JSON string with success status and dropdown update details
    """
    sheets_service, drive_service = _get_google_services()
    return update_dropdown_options_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, action, column_name, dropdown_options)


@mcp.tool()
def delete_table_column_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to delete columns from"),
    column_names: List[str] = Field(..., description="List of column names to delete from the table")
) -> str:
    """
    Delete specific columns from a table in Google Sheets.
    
    This tool removes the specified columns from the table and updates the table structure
    accordingly. The remaining columns will be shifted left to fill the gaps.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete columns from
        column_names: List of column names to delete
    
    Returns:
        JSON string with operation results
    """
    sheets_service, drive_service = _get_google_services()
    return delete_table_column_handler(
        drive_service,
        sheets_service,
        spreadsheet_name,
        sheet_name,
        table_name,
        column_names
    )


@mcp.tool()
def add_table_records_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to add records into"),
    records: List[List[Union[str, int, float, bool, None]]] = Field(..., description="""List of records to add into the table.
    
    Each record must be a list of values matching the table's column structure.
    Values can be strings, numbers, booleans, or None.
    
    EXAMPLE: [
        ['John Doe', 30, 'HR', 50000],
        ['Jane Smith', 25, 'Engineering', 60000],
        ['Bob Johnson', 35, 'Marketing', 55000]
    ]
    """)
) -> str:
    """
    Add records (rows) into a table in Google Sheets at the end.
    
    This tool adds new records into a table at the end using InsertRangeRequest,
    UpdateCellsRequest, and UpdateTableRequest operations. Each record must match the table's column structure.
    Records are automatically formatted according to column types.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to add records into
        records: List of records, where each record is a list of values matching table columns
    
    Returns:
        JSON string with success status and operation details
    """
    sheets_service, drive_service = _get_google_services()
    return add_table_records_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, records)


@mcp.tool()
def get_sheet_cells_by_range_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet to get cells from"),
    start_cell: str = Field(..., description="Starting cell reference (e.g., 'A1', 'B2')"),
    end_cell: str = Field(..., description="Ending cell reference (e.g., 'C5', 'D10')"),
    include_headers: bool = Field(default=False, description="Whether to include header row (default: False)")
) -> str:
    """
    Get sheet cells by range.
    
    This tool retrieves cell data from a specific range within a sheet.
    You can specify the exact cell range using A1 notation.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to get cells from
        start_cell: Starting cell reference (e.g., 'A1', 'B2')
        end_cell: Ending cell reference (e.g., 'C5', 'D10')
        include_headers: Whether to include header row
    
    Returns:
        JSON string with cells data and metadata
    """
    sheets_service, drive_service = _get_google_services()
    return get_sheet_cells_by_range_handler(
        drive_service, 
        sheets_service, 
        spreadsheet_name, 
        sheet_name, 
        start_cell, 
        end_cell, 
        include_headers
    )


@mcp.tool()
def update_table_cells_by_range_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to update"),
    start_cell: str = Field(..., description="Starting cell reference (e.g., 'A1', 'B2')"),
    end_cell: str = Field(..., description="Ending cell reference (e.g., 'C5', 'D10')"),
    cell_values: List[List[Union[str, int, float, bool, None]]] = Field(..., description="""2D array of values to update (rows x columns)
    
    Must match the range dimensions based on start_cell and end_cell.
    
    EXAMPLE: For range 'A1:C2', you need 2 rows x 3 columns:
    [
        ['Value1', 'Value2', 'Value3'],
        ['Value4', 'Value5', 'Value6']
    ]
    """)
) -> str:
    """
    Update table cells by range.
    
    This tool updates cell data in a specific range within a table.
    You can specify the exact cell range using A1 notation.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        start_cell: Starting cell reference (e.g., 'A1', 'B2')
        end_cell: Ending cell reference (e.g., 'C5', 'D10')
        cell_values: 2D array of values to update (rows x columns)
    
    Returns:
        JSON string with update details
    """
    sheets_service, drive_service = _get_google_services()
    return update_table_cells_by_range_handler(
        drive_service, 
        sheets_service, 
        spreadsheet_name, 
        sheet_name, 
        table_name, 
        start_cell, 
        end_cell, 
        cell_values
    )


if __name__ == "__main__":
    mcp.run() 