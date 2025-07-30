# Single Sheet Detailed Metadata Implementation

## Overview

I've enhanced the existing `get_sheet_metadata_handler.py` to provide comprehensive detailed metadata for single sheets, including charts, tables, slicers, drawings, and other embedded objects. The tool now has two modes:

1. **All Sheets Mode**: When no `sheet_name` is provided, returns metadata for all sheets with grid data and formatting
2. **Single Sheet Mode**: When a specific `sheet_name` is provided, returns detailed metadata for that sheet including all embedded objects

## Key Features Added

### ✅ **Enhanced Single Sheet Metadata**
When a specific sheet name is provided, the tool now returns:

#### **Basic Sheet Properties**
- Sheet ID, title, index, and type
- Hidden status and tab color
- Grid properties (row/column counts, frozen panes, gridlines)
- Right-to-left text direction

#### **Charts with Detailed Specifications**
- **Chart Types**: BAR, LINE, PIE, SCATTER, AREA, COLUMN, COMBO, BUBBLE, CANDLESTICK, ORG_CHART, HISTOGRAM, WATERFALL, TREEMAP
- **Chart Information**: Chart ID, position, chart type, and detailed specifications
- **Chart Specifications**: Axis configuration, data domains, series, legend position

#### **Tables with Range Information**
- **Table Properties**: Table ID, name, range, row/column counts
- **Range Details**: Start/end row/column indices
- **Column/Row Properties**: Column and row-specific settings and formatting

#### **Slicers for Interactive Filtering**
- **Slicer Properties**: Slicer ID, position, specifications
- **Data Source**: Associated data source and column index
- **Range Information**: Cell range covered by slicer

#### **Drawings and Visual Elements**
- **Drawing Types**: Shapes, images, lines, word art, embedded charts
- **Drawing Properties**: Drawing ID, position, and type-specific settings

#### **Developer Metadata**
- **Custom Metadata**: Metadata ID, key, value, and visibility settings

## API Implementation

### **Two Different Field Masks**

1. **All Sheets Mode** (when no sheet_name provided):
```python
fields="sheets.properties,sheets.data.rowData,sheets.data.columnMetadata,sheets.data.rowMetadata,sheets.merges,sheets.basicFilter,sheets.charts,sheets.conditionalFormats,sheets.protectedRanges,sheets.developerMetadata"
```

2. **Single Sheet Mode** (when sheet_name provided):
```python
fields="sheets.properties,sheets.charts,sheets.tables,sheets.slicers,sheets.developerMetadata,sheets.drawings"
```

### **Key Functions**

1. **`get_sheet_metadata()`**: Handles all sheets mode with grid data
2. **`get_detailed_sheet_metadata()`**: Handles single sheet mode with detailed metadata
3. **`process_detailed_sheet_metadata()`**: Processes detailed sheet metadata
4. **Processing Functions**: `process_charts()`, `process_tables()`, `process_slicers()`, `process_drawings()`, `process_developer_metadata()`

## Usage Examples

### **Get All Sheets Metadata**
```python
get_sheet_metadata_tool(
    spreadsheet_name="My Spreadsheet"
)
```
Returns: Metadata for all sheets with grid data, formatting, and basic structure

### **Get Detailed Single Sheet Metadata**
```python
get_sheet_metadata_tool(
    spreadsheet_name="My Spreadsheet",
    sheet_name="Sheet1"
)
```
Returns: Comprehensive metadata for the specific sheet including charts, tables, slicers, drawings

## Tool Behavior

### **When `sheet_name` is NOT provided:**
- Returns metadata for all sheets in the spreadsheet
- Includes grid data, row/column metadata, data statistics
- Provides merges, filters, conditional formatting, protected ranges
- Includes basic chart information and developer metadata
- Focuses on grid structure and formatting

### **When `sheet_name` is provided:**
- Returns detailed metadata for the specific sheet only
- Includes comprehensive chart specifications and configurations
- Provides detailed table information with ranges and properties
- Includes slicer information for interactive filtering
- Includes drawings and visual elements
- Focuses on embedded objects and detailed structure

## Response Structure

### **Single Sheet Response**
```json
{
  "success": true,
  "spreadsheet_name": "My Spreadsheet",
  "sheet_name": "Sheet1",
  "metadata": {
    "sheet_id": 0,
    "title": "Sheet1",
    "index": 0,
    "sheet_type": "GRID",
    "hidden": false,
    "grid_properties": {
      "row_count": 1000,
      "column_count": 26,
      "frozen_row_count": 0,
      "frozen_column_count": 0
    },
    "charts": {
      "total_charts": 2,
      "charts": [...],
      "chart_types": ["BAR", "PIE"]
    },
    "tables": {
      "total_tables": 1,
      "tables": [...]
    },
    "slicers": {
      "total_slicers": 1,
      "slicers": [...]
    },
    "drawings": {
      "total_drawings": 0,
      "drawings": []
    },
    "developer_metadata": {
      "total_metadata": 0,
      "metadata": []
    }
  },
  "message": "Successfully retrieved detailed metadata for sheet 'Sheet1' in 'My Spreadsheet'"
}
```

## Benefits

1. **Flexible Usage**: Can get overview of all sheets or detailed analysis of specific sheet
2. **Comprehensive Data**: When targeting a specific sheet, provides the most detailed metadata available
3. **Performance Optimized**: Uses different field masks based on the use case
4. **Backward Compatible**: Existing functionality for all sheets remains unchanged
5. **Error Handling**: Proper error handling for missing spreadsheets or sheets

## Comparison with Other Tools

| Tool | Focus | Data Included | Use Case |
|------|-------|---------------|----------|
| `list_sheets_tool` | Basic sheet info | Sheet names and IDs | Quick overview |
| `get_sheet_metadata_tool` (all sheets) | Sheet-level details | Grid data, formatting | Detailed sheet analysis |
| `get_sheet_metadata_tool` (single sheet) | **Detailed structure** | **All embedded objects** | **Comprehensive analysis** |
| `get_detailed_spreadsheet_metadata_tool` | Spreadsheet-level | All sheets with structure | Complete spreadsheet overview |

This enhancement provides the most comprehensive single-sheet analysis available, making it perfect for detailed sheet analysis and documentation. 