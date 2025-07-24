# Google Sheets MCP - Integrated Tools Plan

## 🎯 **Integrated Approach: Group Related Functions**

Instead of 80+ individual tools, we'll create **15-20 powerful integrated tools** that combine related API functions.

## 📋 **Core Integrated Tools**

### **1. Spreadsheet Management Tool**
**Combines:** GET spreadsheets, POST spreadsheets, PATCH spreadsheets
```python
@mcp.tool()
def manage_spreadsheet(
    action: str,  # "list", "create", "get_info", "update_properties"
    spreadsheet_id: str = None,
    title: str = None,
    properties: dict = None
) -> Union[List[SpreadsheetInfo], SpreadsheetInfo, SpreadsheetMetadata]
```

### **2. Sheet Management Tool**
**Combines:** InsertSheet, DeleteSheet, UpdateSheetProperties, CopyPaste sheets
```python
@mcp.tool()
def manage_sheets(
    action: str,  # "list", "create", "delete", "duplicate", "rename", "move", "copy_to"
    spreadsheet_id: str,
    sheet_id: int = None,
    sheet_name: str = None,
    new_name: str = None,
    target_spreadsheet_id: str = None
) -> Union[List[SheetInfo], SheetInfo, str]
```

### **3. Data Reading Tool**
**Combines:** GET values, GET batchGet, GET spreadsheets (metadata)
```python
@mcp.tool()
def read_data(
    spreadsheet_id: str,
    ranges: List[str] = None,  # ["Sheet1!A1:Z10", "Sheet2!A1:D5"]
    include_formatting: bool = False,
    include_metadata: bool = False
) -> Union[str, List[CellValue], SpreadsheetMetadata]
```

### **4. Data Writing Tool**
**Combines:** PUT values, POST append, POST batchUpdate values
```python
@mcp.tool()
def write_data(
    action: str,  # "write", "append", "batch_update", "clear"
    spreadsheet_id: str,
    range_name: str = None,
    values: List[List[str]] = None,
    ranges_and_values: List[dict] = None
) -> str
```

### **5. Cell Formatting Tool**
**Combines:** UpdateCells, UpdateBorders, MergeCells, UnmergeCells
```python
@mcp.tool()
def format_cells(
    action: str,  # "format", "merge", "unmerge", "borders", "clear_formatting"
    spreadsheet_id: str,
    range_name: str,
    formatting: dict = None,  # {backgroundColor, textFormat, borders, alignment}
    merge_type: str = None  # "MERGE_ALL", "MERGE_COLUMNS", "MERGE_ROWS"
) -> str
```

### **6. Row/Column Management Tool**
**Combines:** InsertDimension, DeleteDimension, UpdateDimensionProperties, AutoResizeDimensions
```python
@mcp.tool()
def manage_dimensions(
    action: str,  # "insert_rows", "insert_columns", "delete_rows", "delete_columns", "resize", "hide", "show"
    spreadsheet_id: str,
    sheet_id: int,
    start_index: int,
    end_index: int = None,
    properties: dict = None  # {width, height, hidden}
) -> str
```

### **7. Data Validation Tool**
**Combines:** SetDataValidation, AddConditionalFormatRule, UpdateConditionalFormatRule
```python
@mcp.tool()
def validate_data(
    action: str,  # "add_validation", "add_conditional_format", "update_conditional_format", "clear_validation"
    spreadsheet_id: str,
    range_name: str,
    validation_rule: dict = None,
    conditional_format: dict = None
) -> str
```

### **8. Filtering & Sorting Tool**
**Combines:** SortRange, AddFilterView, UpdateFilterView, ClearBasicFilter
```python
@mcp.tool()
def filter_and_sort(
    action: str,  # "sort", "add_filter", "update_filter", "clear_filter"
    spreadsheet_id: str,
    range_name: str,
    sort_spec: dict = None,
    filter_spec: dict = None
) -> str
```

### **9. Chart & Visualization Tool**
**Combines:** AddChart, UpdateChartSpec, DeleteChart, AddSlicer
```python
@mcp.tool()
def manage_charts(
    action: str,  # "add_chart", "update_chart", "delete_chart", "add_slicer"
    spreadsheet_id: str,
    chart_id: int = None,
    chart_spec: dict = None,
    position: dict = None
) -> Union[str, ChartInfo]
```

### **10. Protection & Security Tool**
**Combines:** AddProtectedRange, UpdateProtectedRange, DeleteProtectedRange
```python
@mcp.tool()
def manage_protection(
    action: str,  # "protect_range", "update_protection", "remove_protection", "protect_sheet"
    spreadsheet_id: str,
    range_name: str = None,
    sheet_id: int = None,
    protection: dict = None
) -> str
```

### **11. Named Ranges Tool**
**Combines:** UpdateNamedRange, DeleteNamedRange, GET spreadsheets (namedRanges)
```python
@mcp.tool()
def manage_named_ranges(
    action: str,  # "list", "create", "update", "delete"
    spreadsheet_id: str,
    range_name: str = None,
    named_range_id: str = None,
    properties: dict = None
) -> Union[List[NamedRange], NamedRange, str]
```

### **12. Import/Export Tool**
**Combines:** Multiple operations for data import/export
```python
@mcp.tool()
def import_export_data(
    action: str,  # "import_csv", "export_csv", "import_json", "export_pdf"
    spreadsheet_id: str,
    sheet_name: str = None,
    file_path: str = None,
    data: str = None,
    format: str = None
) -> Union[str, bytes]
```

### **13. Search & Analytics Tool**
**Combines:** Search across sheets, analyze data types, find duplicates
```python
@mcp.tool()
def search_and_analyze(
    action: str,  # "search", "analyze_types", "find_duplicates", "get_statistics"
    spreadsheet_id: str,
    query: str = None,
    range_name: str = None,
    analysis_type: str = None
) -> Union[List[SearchResult], dict, str]
```

### **14. Collaboration Tool**
**Combines:** Share spreadsheet, add comments, manage permissions
```python
@mcp.tool()
def collaborate(
    action: str,  # "share", "add_comment", "get_permissions", "update_permissions"
    spreadsheet_id: str,
    user_email: str = None,
    permission: str = None,
    comment: str = None,
    cell_range: str = None
) -> str
```

### **15. Batch Operations Tool**
**Combines:** POST batchUpdate for complex multi-step operations
```python
@mcp.tool()
def batch_operations(
    spreadsheet_id: str,
    operations: List[dict]  # List of operations to perform
) -> BatchUpdateResponse
```

## 📊 **Pydantic Models for Integrated Tools**

### **Core Models:**
```python
class SpreadsheetMetadata(BaseModel):
    properties: dict
    sheets: List[SheetInfo]
    namedRanges: List[NamedRange]
    spreadsheetUrl: str

class CellValue(BaseModel):
    value: str
    formattedValue: str
    userEnteredValue: dict
    effectiveFormat: dict

class FormattingOptions(BaseModel):
    backgroundColor: dict = None
    textFormat: dict = None
    borders: dict = None
    alignment: dict = None

class ValidationRule(BaseModel):
    condition: dict
    inputMessage: str = None
    strict: bool = True

class ChartSpec(BaseModel):
    title: str
    basicChart: dict = None
    pieChart: dict = None
    histogramChart: dict = None

class BatchUpdateResponse(BaseModel):
    responses: List[dict]
    updatedSpreadsheet: SpreadsheetMetadata
```

## 🎯 **Benefits of Integrated Approach**

### **✅ Advantages:**
1. **Fewer Tools** - 15 tools instead of 80+
2. **Better UX** - Related functions grouped together
3. **Easier Maintenance** - Less code to maintain
4. **Consistent Interface** - Similar patterns across tools
5. **Batch Operations** - Multiple related actions in one call

### **📋 Example Usage:**

```python
# Instead of separate tools for create_sheet, rename_sheet, format_sheet
result = await session.call_tool("manage_sheets", {
    "action": "create",
    "spreadsheet_id": "123",
    "sheet_name": "New Sheet"
})

# Then format the new sheet
result = await session.call_tool("format_cells", {
    "action": "format",
    "spreadsheet_id": "123",
    "range_name": "New Sheet!A1:Z1000",
    "formatting": {"backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}
})
```

## 🚀 **Implementation Priority**

### **Phase 1: Core Tools (5 tools)**
1. ✅ `list_spreadsheets` (already implemented)
2. 🔄 `manage_spreadsheet` (integrated create/get/update)
3. 🔄 `manage_sheets` (integrated sheet operations)
4. 🔄 `read_data` (integrated reading)
5. 🔄 `write_data` (integrated writing)

### **Phase 2: Advanced Tools (5 tools)**
6. 🔄 `format_cells` (integrated formatting)
7. 🔄 `manage_dimensions` (integrated row/column operations)
8. 🔄 `filter_and_sort` (integrated filtering)
9. 🔄 `validate_data` (integrated validation)
10. 🔄 `search_and_analyze` (integrated search)

### **Phase 3: Advanced Features (5 tools)**
11. 🔄 `manage_charts` (integrated charts)
12. 🔄 `manage_protection` (integrated protection)
13. 🔄 `manage_named_ranges` (integrated named ranges)
14. 🔄 `collaborate` (integrated sharing)
15. 🔄 `batch_operations` (integrated batch operations)

## 📊 **Summary**

- **From:** 80+ individual API tools
- **To:** 15 integrated, powerful tools
- **Benefit:** Better user experience, easier maintenance
- **Coverage:** All Google Sheets API functionality
- **Flexibility:** Each tool handles multiple related operations

This integrated approach makes the MCP server much more user-friendly while still providing access to all Google Sheets API capabilities! 