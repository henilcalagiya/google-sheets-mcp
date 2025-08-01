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

# Column property models for table creation
class DataValidationRule(BaseModel):
    condition: Dict[str, Any] = Field(..., description="Validation condition with type and values")
    
class ColumnProperty(BaseModel):
    columnName: str = Field(..., description="Name of the column (e.g., 'Employee Name', 'Age', 'Status')")
    columnType: str = Field(..., description="Type of the column: TEXT, NUMBER, DATE, BOOLEAN, PERCENT, CURRENCY")
    dataValidationRule: Optional[DataValidationRule] = Field(default=None, description="Optional data validation rule for dropdown columns with predefined options")

# Local imports - Spreadsheet management handlers
from .handler.spreadsheet.rename_spreadsheet_handler import rename_spreadsheet_handler
from .handler.spreadsheet.get_all_spreadsheets_and_sheets_handler import get_all_spreadsheets_and_sheets_handler

# Local imports - Sheet management handlers

from .handler.sheets.add_sheets_handler import add_sheets_handler
from .handler.sheets.delete_sheets_handler import delete_sheets_handler
from .handler.sheets.duplicate_sheet_handler import duplicate_sheet_handler
from .handler.sheets.rename_sheets_handler import rename_sheets_handler
from .handler.sheets.get_sheet_metadata_handler import get_sheet_metadata_handler


# Local imports - Data reading handlers
from .handler.sheets.read_sheet_data_handler import read_multiple_ranges, read_sheet_data_handler

# Local imports - Content manipulation handlers

from .handler.content_manipulation.insert_dimension_handler import insert_dimension_handler
from .handler.content_manipulation.delete_dimension_handler import delete_dimension
from .handler.content_manipulation.move_dimension_handler import move_dimension
from .handler.content_manipulation.resize_columns_handler import resize_columns_data

# Local imports - Formatting handlers
from .handler.formatting.format_cells_handler import format_cells_data
from .handler.formatting.conditional_format_handler import conditional_format_data
from .handler.formatting.merge_cells_handler import merge_cells_data

# Local imports - Table management handlers
from .handler.tables.add_table_handler import add_table_handler
from .handler.tables.delete_table_handler import delete_table_handler
from .handler.tables.rename_table_handler import rename_table_handler
from .handler.tables.add_table_column_handler import add_table_column_handler
from .handler.tables.modify_column_properties_handler import modify_column_properties_handler
from .handler.tables.delete_table_column_handler import delete_table_column_handler
from .handler.tables.get_table_metadata_handler import get_table_metadata_handler
from .handler.tables.manage_table_records_handler import modify_table_data_handler
from .handler.tables.modify_cell_data_handler import modify_cell_data_handler


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
def get_all_spreadsheets_and_sheets_tool(
    max_spreadsheets: int = Field(default=10, description="Maximum number of spreadsheets to analyze")
) -> str:
    """Get all spreadsheets and their sheets in a simple, clean format."""
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    return get_all_spreadsheets_and_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        max_spreadsheets=max_spreadsheets
    )


@mcp.tool()
def update_spreadsheet_title_tool(
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet to rename"),
    new_title: str = Field(..., description="The new title for the spreadsheet")
) -> str:
    """Rename a Google Spreadsheet."""
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





# =============================================================================
# SHEETS RELATED TOOLS
# =============================================================================




@mcp.tool()
def add_sheets_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_names: List[str] = Field(..., description="List of sheet names to add as new sheets")
) -> str:
    """Add new sheets to a Google Spreadsheet."""
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
    """Delete sheets from a Google Spreadsheet."""
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
    """Duplicate a sheet in a Google Spreadsheet."""
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
    """Rename sheets in a Google Spreadsheet."""
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
    """Read data from multiple ranges in a Google Spreadsheet."""
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
    """Get comprehensive metadata about a specific sheet."""
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
def insert_sheet_dimension(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet"),
    dimension: str = Field(..., description="Dimension to insert: 'ROWS' or 'COLUMNS'"),
    position: int = Field(..., description="Position to insert at (0-based)"),
    count: int = Field(..., description="Number of rows/columns to insert")
) -> str:
    """Insert rows or columns in a Google Spreadsheet."""
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
    """Delete rows or columns from a Google Spreadsheet."""
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
    """Move rows or columns in a Google Spreadsheet."""
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
    """Resize columns in a Google Spreadsheet."""
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
    """Format cells in a Google Spreadsheet."""
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
    """Apply conditional formatting to cells in a Google Spreadsheet."""
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
    """Merge cells in a Google Spreadsheet."""
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
# TABLE MANAGEMENT TOOLS
# =============================================================================


@mcp.tool()
def create_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet to create table in"),
    table_name: str = Field(..., description="A descriptive name for the table (e.g., 'Project Tracker', 'Customer Data')"),
    start_cell: str = Field(..., description="Starting cell for the table (e.g., 'A1')"),
    column_names: List[str] = Field(..., description="List of column names (e.g., ['Employee Name', 'Age', 'Department', 'Salary'])"),
    column_types: List[str] = Field(..., description="""List of column types corresponding to column_names. 
    
    SUPPORTED TYPES:
    - TEXT: Regular text input (names, descriptions, notes)
    - NUMBER: Numeric values (ages, scores, quantities) - formatted as #,##0.00
    - DATE: Date values (birth dates, deadlines, timestamps)
    - TIME: Time values (meeting times, durations) - formatted as hh:mm:ss
    - DATE_TIME: Date and time values (meetings, events) - formatted as yyyy-mm-dd hh:mm:ss
    - BOOLEAN: True/False values (yes/no, active status)
    - PERCENT: Percentage values (completion rates, scores) - formatted as 0.00%
    - CURRENCY: Currency values (prices, budgets, costs) - formatted as $#,##0.00
    - DROPDOWN: Dropdown list with predefined options (use with dropdown_options parameter)
    - NONE: Unspecified type (default formatting, no special validation)
    
    EXAMPLE: ['TEXT', 'NUMBER', 'DROPDOWN', 'CURRENCY'] for ['Employee Name', 'Age', 'Department', 'Salary']
    """),
    dropdown_columns: List[str] = Field(default=[], description="""List of column names that should have dropdown validation.
    
    EXAMPLE: ['Department', 'Status', 'Priority']
    This will create dropdowns for columns named 'Department', 'Status', and 'Priority'.
    """),
    dropdown_values: List[str] = Field(default=[], description="""Comma-separated dropdown options for each dropdown column.
    
    EXAMPLE: ['HR,IT,Sales,Marketing', 'Active,Inactive,Pending', 'Low,Medium,High']
    This provides options for the dropdown columns in the same order as dropdown_columns.
    First dropdown (Department): HR, IT, Sales, Marketing
    Second dropdown (Status): Active, Inactive, Pending  
    Third dropdown (Priority): Low, Medium, High
    """)
) -> str:
    """Create a table in a Google Spreadsheet with headers only.
    
    This tool creates a structured table with proper column types, formatting, and validation rules.
    Each column can have a specific data type and optional validation rules for dropdown lists.
    
    COLUMN TYPE EXAMPLES:
    - TEXT: For names, descriptions, notes
    - NUMBER: For ages, scores, quantities (formatted as #,##0.00)
    - DATE: For dates, deadlines, timestamps
    - BOOLEAN: For yes/no, true/false fields
    - PERCENT: For percentages, completion rates (formatted as 0.00%)
    - CURRENCY: For prices, budgets, costs (formatted as $#,##0.00)
    
    DROPDOWN VALIDATION:
    Use dataValidationRule for columns that should have predefined options.
    Example: Status column with options "Active", "Inactive", "Pending"
    
    TABLE FEATURES:
    - Automatic column formatting based on type
    - Data validation for dropdown columns
    - Proper number formatting for numeric columns
    - Clean table structure with headers
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return add_table_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        start_cell=start_cell,
        column_names=column_names,
        column_types=column_types,
        dropdown_columns=dropdown_columns,
        dropdown_values=dropdown_values
    )


@mcp.tool()
def delete_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the tables"),
    table_names: List[str] = Field(..., description="List of table names to delete (e.g., ['Project Tracker', 'Customer Data', 'Sales Report'])")
) -> str:
    """Delete one or more tables from a Google Spreadsheet.
    
    Removes table structures while preserving underlying data. Supports batch deletion
    of multiple tables in a single operation for efficiency.
    
    USAGE: table_names=["Project Tracker"] or ["Table1", "Table2", "Table3"]
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return delete_table_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_names=table_names
    )


@mcp.tool()
def rename_table_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    old_table_name: str = Field(..., description="Current name of the table to rename"),
    new_table_name: str = Field(..., description="New name for the table")
) -> str:
    """Rename a table in a Google Spreadsheet.
    
    Changes the table name while preserving all data, structure, and formatting.
    The new name must be unique within the sheet.
    
    USAGE: old_table_name="Project Tracker", new_table_name="Updated Project Tracker"
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return rename_table_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        old_table_name=old_table_name,
        new_table_name=new_table_name
    )


@mcp.tool()
def add_table_column_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to add columns to"),
    column_names: List[str] = Field(..., description="List of column names (e.g., ['Status', 'Priority', 'Notes'])"),
    column_types: List[str] = Field(..., description="""List of column types corresponding to column_names.
    
    SUPPORTED TYPES:
    - TEXT: Regular text input (names, descriptions, notes)
    - NUMBER: Numeric values (ages, scores, quantities) - formatted as #,##0.00
    - DATE: Date values (birth dates, deadlines, timestamps)
    - TIME: Time values (meeting times, durations) - formatted as hh:mm:ss
    - DATE_TIME: Date and time values (meetings, events) - formatted as yyyy-mm-dd hh:mm:ss
    - BOOLEAN: True/False values (yes/no, active status)
    - PERCENT: Percentage values (completion rates, scores) - formatted as 0.00%
    - CURRENCY: Currency values (prices, budgets, costs) - formatted as $#,##0.00
    - DROPDOWN: Dropdown list with predefined options (use with dropdown_columns parameter)
    - NONE: Unspecified type (default formatting, no special validation)
    
    EXAMPLE: ['TEXT', 'NUMBER', 'DROPDOWN'] for ['Status', 'Priority', 'Department']
    """),
    positions: List[int] = Field(..., description="List of positions to insert columns (0-based index, None for end)"),
    dropdown_columns: List[str] = Field(default=[], description="""List of column names that should have dropdown validation.
    
    EXAMPLE: ['Department', 'Status', 'Priority']
    This will create dropdowns for columns named 'Department', 'Status', and 'Priority'.
    """),
    dropdown_values: List[str] = Field(default=[], description="""Comma-separated dropdown options for each dropdown column.
    
    EXAMPLE: ['HR,IT,Sales,Marketing', 'Active,Inactive,Pending', 'Low,Medium,High']
    This provides options for the dropdown columns in the same order as dropdown_columns.
    First dropdown (Department): HR, IT, Sales, Marketing
    Second dropdown (Status): Active, Inactive, Pending  
    Third dropdown (Priority): Low, Medium, High
    """)
) -> str:
    """Add new columns to an existing table in Google Sheets.
    
    Adds columns with specified types, formatting, and optional dropdown validation.
    The columns can be inserted at specific positions or added at the end.
    
    USAGE: Add status and priority columns with dropdown options to project tracker table
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return add_table_column_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        column_names=column_names,
        column_types=column_types,
        positions=positions,
        dropdown_columns=dropdown_columns,
        dropdown_values=dropdown_values
    )


@mcp.tool()
def delete_table_column_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to delete columns from"),
    column_names: List[str] = Field(..., description="List of column names to delete (e.g., ['Status', 'Priority', 'Notes']). Pass the actual column names, not positions or indices.")
) -> str:
    """Delete columns from an existing table in Google Sheets.
    
    Removes specified columns from a table while preserving the remaining structure.
    Cannot delete all columns - at least one column must remain in the table.
    
    USAGE: Delete status and priority columns from project tracker table
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return delete_table_column_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        column_names=column_names
    )


@mcp.tool()
def modify_column_properties_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table containing the column"),
    column_name: str = Field(..., description="Name of the column to change"),
    new_column_name: str = Field(default="", description="New name for the column else must pass empty string"),
    new_column_type: str = Field(default="", description="""New type for the column else must pass empty string.
    
    SUPPORTED TYPES:
    - TEXT: Regular text input (names, descriptions, notes)
    - NUMBER: Numeric values (ages, scores, quantities) - formatted as #,##0.00
    - DATE: Date values (birth dates, deadlines, timestamps)
    - TIME: Time values (meeting times, durations) - formatted as hh:mm:ss
    - DATE_TIME: Date and time values (meetings, events) - formatted as yyyy-mm-dd hh:mm:ss
    - BOOLEAN: True/False values (yes/no, active status)
    - PERCENT: Percentage values (completion rates, scores) - formatted as 0.00%
    - CURRENCY: Currency values (prices, budgets, costs) - formatted as $#,##0.00
    - DROPDOWN: Dropdown list with predefined options
    - NONE: Unspecified type (default formatting, no special validation)
    """),
    new_dropdown_options: List[str] = Field(default=[], description="New dropdown options else must pass empty list (e.g., ['Active', 'Inactive', 'Pending'])"),
    remove_dropdown: bool = Field(default=False, description="Whether to remove dropdown validation (default: False)"),
    add_dropdown_options: List[str] = Field(default=[], description="Options to add to existing dropdown else must pass empty list (e.g., ['New Option 1', 'New Option 2'])"),
    remove_dropdown_options: List[str] = Field(default=[], description="Specific options to remove from dropdown else must pass empty list (e.g., ['Old Option 1', 'Old Option 2'])")
) -> str:
    """Modify properties of an existing column in a table in Google Sheets.
    
    Allows changing column name, type, dropdown options, or removing dropdown validation.
    At least one property must be specified for change.
    
    USAGE: Modify column name, type, or dropdown options
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return modify_column_properties_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        column_name=column_name,
        new_column_name=new_column_name,
        new_column_type=new_column_type,
        new_dropdown_options=new_dropdown_options,
        remove_dropdown=remove_dropdown,
        add_dropdown_options=add_dropdown_options,
        remove_dropdown_options=remove_dropdown_options
    )


@mcp.tool()
def get_table_metadata_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to get metadata for")
) -> str:
    """Get comprehensive metadata for a specific table in Google Sheets.
    
    Retrieves detailed information about a table including:
    - Table ID and name
    - Dimensions (row count, column count)
    - Range boundaries (start/end row/column indices)
    - Range notation in A1 format
    - Associated spreadsheet and sheet information
    
    USAGE: Get metadata for "Project Tracker" table in "Sheet1" of "My Spreadsheet"
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return get_table_metadata_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name
    )


@mcp.tool()
def manage_table_records_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to modify"),
    operation: str = Field(..., description="""Type of operation to perform:
    
    - append: Add rows at the end of the table
    - insert: Insert rows at a specific position
    - remove: Remove specific rows from the table
    """),
    data: List[List[str]] = Field(default=[], description="""List of rows to add/insert (for append/insert operations).
    
    Each row should be a list of string values corresponding to the table columns.
    EXAMPLE: [['John Doe', '30', 'HR', '50000'], ['Jane Smith', '25', 'IT', '60000']]
    """),
    row_index: int = Field(default=None, description="Row index for insert operation (0-based for data rows only, header row is excluded)"),
    row_indices: List[int] = Field(default=[], description="List of row indices to remove (0-based for data rows only, header row is excluded)")
) -> str:
    """Manage records in a table in Google Sheets.
    
    Allows appending, inserting, or removing rows from existing tables.
    
    USAGE: 
    - Append new employee records to table
    - Insert records at specific positions
    - Remove outdated or duplicate records
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return modify_table_data_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        operation=operation,
        data=data,
        row_index=row_index,
        row_indices=row_indices
    )


@mcp.tool()
def modify_cell_data_tool(
    spreadsheet_name: str = Field(..., description="The name of the Google Spreadsheet"),
    sheet_name: str = Field(..., description="The name of the sheet containing the table"),
    table_name: str = Field(..., description="Name of the table to modify"),
    cell_locations: List[str] = Field(..., description="""List of cell locations to update (e.g., ['A2', 'B3', 'C1']).
    
    Use standard Excel notation: A1, B2, C3, etc.
    Row numbers start from 1 (not 0-based).
    """),
    cell_values: List[str] = Field(..., description="""List of new values for the cells (e.g., ['New Name', '42', 'Updated Value']).
    
    Must have the same number of values as cell_locations.
    """)
) -> str:
    """Modify specific cells in a table in Google Sheets.
    
    Allows updating individual cells or multiple cells in a table.
    
    USAGE: Update specific cell values without affecting other data
    """
    if not drive_service:
        raise RuntimeError("Google Drive service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    if not sheets_service:
        raise RuntimeError("Google Sheets service not initialized. Set GOOGLE_CREDENTIALS_PATH.")
    
    return modify_cell_data_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        table_name=table_name,
        cell_locations=cell_locations,
        cell_values=cell_values
    )


# =============================================================================
# OTHERS
# =============================================================================

# No additional tools in this category currently


if __name__ == "__main__":
    mcp.run() 