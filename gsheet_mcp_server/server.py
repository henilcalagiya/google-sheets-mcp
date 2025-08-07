"""Google Sheets MCP Server using FastMCP - Simplified Version."""

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
from .handler.spreadsheet.rename_spreadsheet_handler import rename_spreadsheet_handler
from .handler.spreadsheet.list_spreadsheets_and_sheets_handler import list_spreadsheets_and_sheets_handler

# Local imports - Sheets handlers
from .handler.sheets.add_sheets_handler import add_sheets_handler
from .handler.sheets.delete_sheets_handler import delete_sheets_handler
from .handler.sheets.duplicate_sheet_handler import duplicate_sheet_handler
from .handler.sheets.rename_sheets_handler import rename_sheets_handler
from .handler.sheets.analyze_sheet_handler import analyze_sheet_handler

# Local imports - Table management handlers
from .handler.tables.create_table_handler import create_table_handler
from .handler.tables.delete_table_handler import delete_table_handler
from .handler.tables.rename_table_handler import rename_table_handler
from .handler.tables.get_table_metadata_handler import get_table_metadata_handler
from .handler.tables.add_table_column_handler import add_table_column_handler


from .handler.tables.update_table_sorting_handler import update_table_sorting_handler
from .handler.tables.clear_table_data_handler import clear_table_data_handler
from .handler.tables.delete_table_records_handler import delete_table_records_handler
from .handler.tables.get_table_rows_handler import get_table_rows_handler
from .handler.tables.update_table_row_handler import update_table_row_handler
from .handler.tables.update_table_cells_handler import update_table_cells_handler
from .handler.tables.find_table_cells_handler import find_table_cells_handler
from .handler.tables.rename_table_column_handler import rename_table_column_handler
from .handler.tables.change_table_column_type_handler import change_table_column_type_handler
from .handler.tables.manage_column_properties_handler import manage_column_properties_handler
from .handler.tables.toggle_table_footer_handler import toggle_table_footer_handler
from .handler.tables.read_table_data_handler import read_table_data_handler
from .handler.tables.get_table_data_by_columns_handler import get_table_data_by_columns_handler
from .handler.tables.get_table_data_handler import get_table_data_handler
from .handler.tables.manage_dropdown_options_handler import manage_dropdown_options_handler
from .handler.tables.delete_table_column_handler import delete_table_column_handler

from .handler.tables.insert_table_records_handler import insert_table_records_handler

# Create an MCP server
mcp = FastMCP("Google Sheets MCP")


def _setup_google_services_from_env():
    """Set up Google Sheets and Drive API services from environment variables."""
    try:
        # Get all credential components from environment variables
        project_id = os.getenv("GOOGLE_PROJECT_ID")
        private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID")
        private_key = os.getenv("GOOGLE_PRIVATE_KEY")
        client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        auth_uri = os.getenv("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
        token_uri = os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token")
        auth_provider_x509_cert_url = os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
        client_x509_cert_url = os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
        
        # Validate required fields
        required_fields = {
            "GOOGLE_PROJECT_ID": project_id,
            "GOOGLE_PRIVATE_KEY_ID": private_key_id,
            "GOOGLE_PRIVATE_KEY": private_key,
            "GOOGLE_CLIENT_EMAIL": client_email,
            "GOOGLE_CLIENT_ID": client_id,
            "GOOGLE_CLIENT_X509_CERT_URL": client_x509_cert_url
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

# Removed _setup_google_services function - using environment variables only


# Initialize services using environment variables only
try:
    sheets_service, drive_service = _setup_google_services_from_env()
    print("✅ Google services initialized from environment variables")
except Exception as env_error:
    print(f"❌ Failed to initialize Google services from environment variables: {env_error}")
    print("📋 Required environment variables:")
    print("  - GOOGLE_PROJECT_ID")
    print("  - GOOGLE_PRIVATE_KEY_ID") 
    print("  - GOOGLE_PRIVATE_KEY")
    print("  - GOOGLE_CLIENT_EMAIL")
    print("  - GOOGLE_CLIENT_ID")
    print("  - GOOGLE_CLIENT_X509_CERT_URL")
    print("\n💡 Use the helper script to extract from your credentials file:")
    print("  python3 update_mcp_config.py path/to/your/credentials.json")
    raise ValueError("Google credentials environment variables are required")


@mcp.tool()
def list_spreadsheets_and_sheets_tool(
    max_spreadsheets: int = Field(default=10, description="Maximum number of spreadsheets to analyze")
) -> str:
    """
    Discover spreadsheets and their sheet names.
    
    Args:
        max_spreadsheets: Maximum number of spreadsheets to analyze (default: 10)
    
    Returns:
        JSON string containing spreadsheet names and their sheet names
    """
    return list_spreadsheets_and_sheets_handler(
        drive_service, sheets_service, max_spreadsheets
    )


@mcp.tool()
def rename_spreadsheet_title_tool(
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet to rename"),
    new_title: str = Field(..., description="The new title for the spreadsheet")
) -> str:
    """
    Rename a Google Spreadsheet.
    """
    return rename_spreadsheet_handler(drive_service, sheets_service, spreadsheet_name, new_title)


@mcp.tool()
def add_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to add as new sheets")
) -> str:
    """
    Add new sheets to a Google Spreadsheet.
    """
    return add_sheets_handler(drive_service, sheets_service, spreadsheet_name, sheet_names)


@mcp.tool()
def delete_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to delete")
) -> str:
    """
    Delete sheets from a Google Spreadsheet.
    """
    return delete_sheets_handler(drive_service, sheets_service, spreadsheet_name, sheet_names)


@mcp.tool()
def duplicate_sheet_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    source_sheet_name: str = Field(..., description="Name of the sheet to duplicate"),
    new_sheet_name: str = Field(default="", description="Name for the duplicated sheet (optional, will auto-generate if not provided)"),
    insert_position: int = Field(default=None, description="Position to insert the duplicated sheet (1-based index, optional - will insert at end if not specified)")
) -> str:
    """
    Duplicate an existing sheet.
    """
    return duplicate_sheet_handler(drive_service, sheets_service, spreadsheet_name, source_sheet_name, new_sheet_name, insert_position)


@mcp.tool()
def rename_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to rename (put only the names of the sheets you want to rename)"),
    new_titles: List[str] = Field(..., description="List of new titles for the sheets")
) -> str:
    """
    Rename sheets in a Google Spreadsheet.
    """
    return rename_sheets_handler(drive_service, sheets_service, spreadsheet_name, sheet_names, new_titles)


@mcp.tool()
def analyze_sheet_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="Name of the specific sheet to analyze")
) -> str:
    """
    Analyze a specific sheet's contents and structure.
    
    This tool provides detailed analysis of a sheet's contents, including:
    - Data distribution and patterns
    - Cell types and formatting
    - Empty vs. filled cells
    - Potential data structures
    - Complexity assessment
    
    Args:
        spreadsheet_name: The name of the Google Spreadsheet
        sheet_name: Name of the specific sheet to analyze
    
    Returns:
        JSON string with comprehensive analysis results
    """
    return analyze_sheet_handler(drive_service, sheets_service, spreadsheet_name, sheet_name)


# Table Management Tools

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
    return delete_table_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_names)


@mcp.tool()
def rename_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    old_table_name: str = Field(..., description="Current name of the table to rename"),
    new_table_name: str = Field(..., description="New name for the table")
) -> str:
    """
    Rename a table in Google Sheets.
    
    This tool allows you to change the name of an existing table.
    The table structure and data remain unchanged.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        old_table_name: Current name of the table
        new_table_name: New name for the table
    
    Returns:
        JSON string with success status and rename details
    """
    return rename_table_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, old_table_name, new_table_name)


@mcp.tool()
def get_table_metadata_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(default=None, description="Name of the table to get metadata for. If not provided, returns metadata for all tables in the sheet.")
) -> str:
    """
    Get comprehensive metadata for tables in Google Sheets.
    
    This tool provides detailed information about table structure, columns, data types,
    and other properties. If no table name is provided, returns metadata for all tables.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to get metadata for (optional)
    
    Returns:
        JSON string containing table metadata or list of all tables
    """
    return get_table_metadata_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name)


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
    return update_table_sorting_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_name, sort_order)


@mcp.tool()
def clear_table_data_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to clear data from")
) -> str:
    """
    Clear all data from a table while preserving the table structure.
    
    This tool removes all data rows from a table while keeping the table structure,
    column definitions, and formatting intact.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to clear data from
    
    Returns:
        JSON string with success status and clearing details
    """
    return clear_table_data_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name)


@mcp.tool()
def delete_table_records_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to delete records from"),
    row_indices: List[int] = Field(..., description="List of row indices to delete (1-based, excluding header)")
) -> str:
    """
    Delete specific records (rows) from a table.
    
    This tool removes specific records from a table while preserving the table structure.
    Row indices are 1-based and exclude the header row.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to delete records from
        row_indices: List of row indices to delete (1-based, excluding header)
    
    Returns:
        JSON string with success status and deletion details
    """
    return delete_table_records_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, row_indices)

@mcp.tool()
def update_table_row_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to update"),
    row_index: int = Field(..., description="Row index to update (1-based, excluding header)"),
    data: List[Union[str, int, float, bool, None]] = Field(..., description="""List of values for the entire row.
    
    Must match the number of columns in the table.
    Values can be strings, numbers, booleans, or None.
    EXAMPLE: ['John Doe', 30, 'HR', 50000]
    """)
) -> str:
    """
    Update an entire row in a table.
    
    This tool updates all cells in a specific row with new values.
    The data must match the number of columns in the table.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to update
        row_index: Row index to update (1-based, excluding header)
        data: List of values for the entire row
    
    Returns:
        JSON string with success status and update details
    """
    return update_table_row_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, row_index, data)


# @mcp.tool()
# def update_table_cells_tool(
#     spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
#     sheet_name: str = Field(..., description="The name of the sheet containing the table"),
#     table_name: str = Field(..., description="Name of the table to update"),
#     cell_updates: List[Dict[str, Union[str, int, float, bool, None]]] = Field(..., description="""List of cell updates, each containing:
#     - row_index: Row index (1-based, excluding header)
#     - column_index: Column index (1-based)
#     - value: New value for the cell (string, number, boolean, or None)
    
#     For single cell: [{"row_index": 1, "column_index": 2, "value": "New Value"}]
#     For multiple cells: [{"row_index": 1, "column_index": 2, "value": "Value1"}, {"row_index": 2, "column_index": 3, "value": 50000}]
#     """)
# ) -> str:
#     """
#     Update single or multiple cells in a table.
    
#     This tool updates specific cells in a table with new values.
#     Can handle both single cell updates and batch cell updates efficiently.
#     Each cell update must specify row index, column index, and new value.
    
#     Args:
#         spreadsheet_name: Name of the spreadsheet
#         sheet_name: Name of the sheet containing the table
#         table_name: Name of the table to update
#         cell_updates: List of cell updates with row_index, column_index, and value
    
#     Returns:
#         JSON string with success status and update details
#     """
#     return update_table_cells_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, cell_updates)


# @mcp.tool()
# def find_table_cells_tool(
#     spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
#     sheet_name: str = Field(..., description="The name of the sheet containing the table"),
#     table_name: str = Field(..., description="Name of the table to search in"),
#     search_value: Union[str, int, float, bool] = Field(..., description="Value to search for"),
#     search_type: str = Field(default="exact", description="Type of search: 'exact', 'contains', 'starts_with', 'ends_with' (default: 'exact')"),
#     case_sensitive: bool = Field(default=False, description="Whether search should be case sensitive (default: False)"),
#     include_headers: bool = Field(default=False, description="Whether to include header row in search (default: False)")
# ) -> str:
#     """
#     Find specific values in table cells.
    
#     This tool searches for values in table cells using various search methods.
#     You can search for exact matches, partial matches, or pattern matches.
    
#     Args:
#         spreadsheet_name: Name of the spreadsheet
#         sheet_name: Name of the sheet containing the table
#         table_name: Name of the table to search in
#         search_value: Value to search for
#         search_type: Type of search - "exact", "contains", "starts_with", "ends_with"
#         case_sensitive: Whether search should be case sensitive
#         include_headers: Whether to include header row in search
    
#     Returns:
#         JSON string with found cells data and metadata
#     """
#     return find_table_cells_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, search_value, search_type, case_sensitive, include_headers)


@mcp.tool()
def rename_table_column_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to rename columns in"),
    column_indices: List[int] = Field(..., description="List of column indices to rename (0-based)"),
    new_column_names: List[str] = Field(..., description="List of new column names (must match column_indices count)")
) -> str:
    """
    Rename columns in a table.
    
    This tool renames existing columns in a table by their index.
    The number of column indices must match the number of new column names.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to rename columns in
        column_indices: List of column indices to rename (0-based)
        new_column_names: List of new column names
    
    Returns:
        JSON string with success status and rename details
    """
    return rename_table_column_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_indices, new_column_names)


@mcp.tool()
def change_table_column_type_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to change column types in"),
    column_names: List[str] = Field(..., description="List of column names to change types for"),
    new_column_types: List[str] = Field(..., description="List of new column types (must match column_names count)")
) -> str:
    """
    Change column types in a table.
    
    This tool changes the data type of existing columns in a table.
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
        table_name: Name of the table to change column types in
        column_names: List of column names to change types for
        new_column_types: List of new column types
    
    Returns:
        JSON string with success status and type change details
    """
    return change_table_column_type_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_names, new_column_types)



@mcp.tool()
def toggle_table_footer_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to toggle footer for"),
    action: str = Field(..., description="Action to perform: 'add' or 'remove'")
) -> str:
    """
    Toggle table footer in Google Sheets.
    
    This tool can add or remove a footer row from a table by updating the table range.
    Adding a footer extends the table by one row at the bottom.
    Removing a footer reduces the table by one row from the bottom.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to toggle footer for
        action: Action to perform - "add" or "remove"
    
    Returns:
        JSON string with success status and toggle details
    """
    return toggle_table_footer_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, action)



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
    return get_table_data_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, column_names, start_row, end_row, include_headers, max_rows)


@mcp.tool()
def manage_dropdown_options_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to manage dropdown options in"),
    action: str = Field(..., description="Action to perform: 'add' or 'remove'"),
    column_names: List[str] = Field(..., description="List of column names to manage dropdown options for"),
    dropdown_options: Optional[List[List[str]]] = Field(default=[], description="List of dropdown options to add/remove for each column (required for 'add' and 'remove' actions)")
) -> str:
    """
    Manage dropdown options in table columns.
    
    This tool can add or remove specific dropdown options from existing columns in a table.
    For 'add' action: Adds new options to existing dropdown (preserves existing options).
    For 'remove' action: Removes specific options from existing dropdown.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to manage dropdown options in
        action: Action to perform - "add" or "remove"
        column_names: List of column names to manage dropdown options for
        dropdown_options: List of dropdown options to add/remove for each column
    
    Returns:
        JSON string with success status and dropdown management details
    """
    return manage_dropdown_options_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, action, column_names, dropdown_options)


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
    return delete_table_column_handler(
        drive_service,
        sheets_service,
        spreadsheet_name,
        sheet_name,
        table_name,
        column_names
    )


@mcp.tool()
def insert_table_records_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to insert records into"),
    records: List[List[Union[str, int, float, bool, None]]] = Field(..., description="""List of records to insert into the table.
    
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
    Insert records (rows) into a table in Google Sheets at the end.
    
    This tool inserts new records into a table at the end using InsertRangeRequest,
    UpdateCellsRequest, and UpdateTableRequest operations. Each record must match the table's column structure.
    Records are automatically formatted according to column types.
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet containing the table
        table_name: Name of the table to insert records into
        records: List of records, where each record is a list of values matching table columns
    
    Returns:
        JSON string with success status and operation details
    """
    return insert_table_records_handler(drive_service, sheets_service, spreadsheet_name, sheet_name, table_name, records)


if __name__ == "__main__":
    mcp.run() 