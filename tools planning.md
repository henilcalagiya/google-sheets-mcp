# Google Sheets MCP Server - Complete Tools List

## 📋 Spreadsheet Management Tools (2 tools)

### Spreadsheet Operations
1. `discover_spreadsheets_contents_tool`🟢 - Discover and analyze all spreadsheets
2. `rename_spreadsheet_title_tool`🟢 - Rename a Google Spreadsheet

## 📄 Sheet Management Tools (5 tools)

### Sheet Operations
3. `add_sheets_tool`🟢 - Add new sheets to a spreadsheet
4. `delete_sheets_tool`🟢 - Delete sheets from a spreadsheet
5. `duplicate_sheet_tool`🟢 - Create a copy of an existing sheet
6. `rename_sheets_tool`🟢 - Rename sheets in a spreadsheet
7. `analyze_sheet_tool`🟢 - Analyze sheet structure and content

## 📊 Table Management Tools (20 tools)

### Core Table Operations
8. `create_table_tool`🟢 - Create a new table with specified columns and data types
9. `delete_table_tool`🟢 - Delete one or more tables from a sheet
10. `rename_table_tool`🟢 - Rename an existing table
11. `get_table_metadata_tool`🟢 - Get comprehensive metadata about tables

### Table Structure Management
12. `add_table_column_tool`🟢 - Add new columns to existing table
13. `delete_table_column_tool`🟢 - Remove columns from table
14. `rename_table_column_tool`🟢 - Rename table columns
15. `change_table_column_type_tool`🟢 - Modify column data types

### Table Data Operations
16. `insert_table_records_tool`🟢 - Insert records at end of table
17. `delete_table_records_tool`🟢 - Delete specific records from table
18. `get_table_rows_tool`🟢 - Retrieve table data rows
19. `update_table_row_tool`🟢 - Update entire row data
20. `clear_table_data_tool`🟢 - Clear all data from table (keep structure)

### Cell-Level Operations
21. `update_table_cells_tool` - Update single or multiple cells in batch

### Data Validation & Dropdowns
23. `manage_dropdown_options_tool`🟢 - Add or remove dropdown options from columns

### Table Sorting
25. `sort_table_by_columns_tool` - Sort table by specific columns

### Cell Search
26. `find_table_cells_tool` - Search for specific values in table

---

**Total: 27 tools implemented and ready for use**

## 🎯 Available Column Types
- DOUBLE: Numeric data with decimals
- CURRENCY: Monetary values ($#,##0.00)
- PERCENT: Percentage values (0.00%)
- DATE: Date values (yyyy-mm-dd)
- TIME: Time values (hh:mm:ss)
- DATE_TIME: Date and time values
- TEXT: Plain text data
- BOOLEAN: True/false values
- DROPDOWN: Selection from predefined options

## 🔧 API Compliance
All tools use the correct Google Sheets API v4 endpoints:
- `updateTable` - For table structure changes
- `updateCells` - For cell value updates
- `insertDimension` - For inserting rows/columns
- `deleteDimension` - For removing rows/columns
- `moveDimension` - For reordering columns
- `appendCells` - For adding rows to tables
- `values().get()` - For retrieving data
- `batchUpdate` - For complex operations
