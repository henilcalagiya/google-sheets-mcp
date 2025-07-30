# Detailed Spreadsheet Metadata Tool

## Overview

The `get_detailed_spreadsheet_metadata_tool` is a comprehensive tool that retrieves complete metadata about a Google Spreadsheet, including all sheets, charts, tables, pivot tables, slicers, and embedded objects. This tool provides the most detailed structural information available through the Google Sheets API.

## Tool Information

- **Tool Name**: `get_detailed_spreadsheet_metadata_tool`
- **Parameters**: 
  - `spreadsheet_name` (str): The name of the Google Spreadsheet to analyze
- **Returns**: Comprehensive metadata dictionary containing all spreadsheet structure information

## What It Provides

### 1. Spreadsheet-Level Metadata
- **Spreadsheet ID**: Unique identifier for the spreadsheet
- **Properties**: Title, locale, timeZone, defaultCellFormat
- **Named Ranges**: Any named ranges defined in the spreadsheet
- **Developer Metadata**: Spreadsheet-scoped custom metadata tags

### 2. Sheet-Level Metadata
For each sheet (tab) in the spreadsheet:

#### Basic Properties
- **Sheet ID**: Unique identifier for the sheet
- **Title**: Name of the sheet
- **Index**: Position of the sheet (0-based)
- **Sheet Type**: GRID, OBJECT, or DATA_SOURCE
- **Hidden Status**: Whether the sheet is hidden
- **Tab Color**: Color styling of the tab
- **Right-to-Left**: Text direction setting

#### Grid Properties
- **Row Count**: Total number of rows
- **Column Count**: Total number of columns
- **Frozen Rows/Columns**: Number of frozen panes
- **Gridlines**: Whether gridlines are hidden
- **Group Controls**: Row/column grouping settings

### 3. Charts
Detailed information about all charts in each sheet:

#### Chart Types Supported
- **Basic Charts**: BAR, LINE, PIE, SCATTER, AREA, COLUMN, COMBO
- **Specialized Charts**: 
  - PIE_CHART
  - BUBBLE_CHART
  - CANDLESTICK_CHART
  - ORG_CHART
  - HISTOGRAM_CHART
  - WATERFALL_CHART
  - TREEMAP_CHART

#### Chart Information
- **Chart ID**: Unique identifier
- **Position**: Location on the sheet
- **Chart Type**: Type of chart
- **Chart Specifications**: 
  - Axis configuration
  - Data domains and series
  - Legend position
  - Chart-specific settings

### 4. Tables
Information about native Google Sheets tables:

- **Table ID**: Unique identifier
- **Table Name**: Human-readable name
- **Range**: Cell range covered by the table
- **Row/Column Counts**: Table dimensions calculated from range
- **Start/End Positions**: Row and column boundaries
- **Column Properties**: Column-specific settings and formatting
- **Row Properties**: Row-specific settings and formatting



### 6. Slicers
Interactive filtering components:

- **Slicer ID**: Unique identifier
- **Position**: Location on the sheet
- **Specifications**: Slicer configuration
- **Data Source ID**: Associated data source
- **Column Index**: Target column
- **Range**: Cell range covered by slicer

### 7. Drawings
Visual elements on sheets:

- **Drawing ID**: Unique identifier
- **Position**: Location on the sheet
- **Shape Properties**: Shape-specific settings
- **Image Properties**: Image-specific settings
- **Line Properties**: Line-specific settings
- **Word Art Properties**: Text art settings
- **Chart Properties**: Embedded chart settings



### 9. Developer Metadata
Custom metadata tags:

- **Metadata ID**: Unique identifier
- **Metadata Key**: Custom key
- **Metadata Value**: Custom value
- **Visibility**: DOCUMENT, PROJECT, or SHEET level

## Summary Statistics

The tool provides comprehensive summary statistics:

- **Total Sheets**: Number of sheets in the spreadsheet
- **Total Charts**: Total number of charts across all sheets
- **Total Tables**: Total number of data source tables
- **Total Slicers**: Total number of slicers
- **Total Drawings**: Total number of drawings
- **Chart Type Distribution**: Count of each chart type
- **Sheets with Charts**: Number of sheets containing charts
- **Sheets with Tables**: Number of sheets containing tables
- **Sheets with Slicers**: Number of sheets containing slicers
- **Hidden Sheets**: Number of hidden sheets
- **Named Ranges Count**: Number of named ranges
- **Developer Metadata Count**: Number of developer metadata entries

## API Endpoint Used

The tool uses the Google Sheets API endpoint:
```
GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}
```

With the field mask:
```
spreadsheetId,properties,namedRanges,developerMetadata,sheets(properties,charts,tables,slicers,developerMetadata,drawings)
```

## Key Features

1. **Comprehensive Coverage**: Retrieves metadata for all major spreadsheet components
2. **No Grid Data**: Excludes cell content to focus on structure and metadata
3. **Detailed Chart Analysis**: Provides complete chart specifications and configurations
4. **Table Information**: Includes native Google Sheets tables with range and properties
5. **Interactive Elements**: Slicer information for filtering components
7. **Visual Elements**: Drawing details
8. **Custom Metadata**: Developer metadata and named ranges
9. **Summary Statistics**: Comprehensive overview of spreadsheet structure

## Usage Examples

### Basic Usage
```python
# Get detailed metadata for a spreadsheet
result = get_detailed_spreadsheet_metadata_tool(
    spreadsheet_name="My Spreadsheet"
)
```

### Expected Response Structure
```json
{
  "success": true,
  "spreadsheet_name": "My Spreadsheet",
  "metadata": {
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "properties": {
      "title": "My Spreadsheet",
      "locale": "en_US",
      "timeZone": "America/New_York"
    },
    "named_ranges": [],
    "developer_metadata": [],
    "sheets": [
      {
        "sheet_id": 0,
        "title": "Sheet1",
        "charts": {
          "total_charts": 2,
          "charts": [...],
          "chart_types": ["BAR", "PIE"]
        },
        "data_source_tables": {
          "total_tables": 1,
          "tables": [...]
        },
        "pivot_tables": {
          "total_pivot_tables": 0,
          "pivot_tables": []
        },
        "slicers": {
          "total_slicers": 1,
          "slicers": [...]
        },
        "drawings": {
          "total_drawings": 0,
          "drawings": []
        },
        "embedded_objects": {
          "total_embedded_objects": 0,
          "embedded_objects": []
        }
      }
    ],
    "summary": {
      "total_sheets": 1,
      "total_charts": 2,
      "total_tables": 1,
      "total_pivot_tables": 0,
      "total_slicers": 1,
      "chart_type_distribution": {
        "BAR": 1,
        "PIE": 1
      },
      "sheets_with_charts": 1,
      "sheets_with_tables": 1,
      "sheets_with_slicers": 1
    }
  },
  "message": "Successfully retrieved detailed metadata for spreadsheet 'My Spreadsheet'"
}
```

## Error Handling

The tool handles various error scenarios:

- **Spreadsheet Not Found**: Returns error if spreadsheet name doesn't exist
- **API Errors**: Handles Google Sheets API errors gracefully
- **Authentication Issues**: Reports credential problems
- **Network Issues**: Handles connection problems

## Comparison with Other Tools

| Tool | Focus | Data Included | Use Case |
|------|-------|---------------|----------|
| `list_sheets_tool` | Basic sheet info | Sheet names and IDs | Quick overview |
| `get_sheet_metadata_tool` | Sheet-level details | Grid data, formatting | Detailed sheet analysis |
| `get_detailed_spreadsheet_metadata_tool` | Complete structure | All embedded objects | Comprehensive analysis |

## Best Practices

1. **Use for Analysis**: Perfect for understanding spreadsheet structure
2. **Performance**: Excludes grid data for faster retrieval
3. **Comprehensive**: Use when you need complete metadata
4. **Documentation**: Great for documenting spreadsheet structure
5. **Audit**: Useful for auditing spreadsheet components

## Technical Notes

- **Field Mask**: Uses optimized field mask to exclude unnecessary data
- **Chart Types**: Supports all Google Sheets chart types
- **Data Sources**: Handles BigQuery and other data source connections
- **Embedded Objects**: Includes images, shapes, and other visual elements
- **Developer Metadata**: Supports custom metadata for advanced use cases

This tool provides the most comprehensive metadata available through the Google Sheets API, making it ideal for spreadsheet analysis, documentation, and auditing purposes. 