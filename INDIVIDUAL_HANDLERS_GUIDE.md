# Individual Handlers Guide

## Overview

This document describes the individual handler files created for each Google Sheets tool. Each handler is focused on a single, specific operation, making the codebase more modular and easier to maintain.

## Handler Files Structure

### 📝 **Write Operations Handlers**

#### 1. `write_cell_handler.py`
**Purpose**: Write a single value to a specific cell
**Function**: `write_cell_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `cell`: Cell reference (e.g., 'Sheet1!A1')
- `value`: Value to write to the cell

**Example**:
```python
result = write_cell_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    cell="Sheet1!A1",
    value="Hello World"
)
```

#### 2. `write_row_handler.py`
**Purpose**: Write a list of values to a row
**Function**: `write_row_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `row_range`: Row range (e.g., 'Sheet1!A1:Z1')
- `values`: List of values to write to the row

**Example**:
```python
result = write_row_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    row_range="Sheet1!A1:E1",
    values=["Name", "Email", "Phone", "Age", "City"]
)
```

#### 3. `write_grid_handler.py`
**Purpose**: Write a 2D array of values to a grid range
**Function**: `write_grid_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `grid_range`: Grid range (e.g., 'Sheet1!A1:C10')
- `values`: 2D array of values to write to the grid

**Example**:
```python
result = write_grid_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    grid_range="Sheet1!A1:C3",
    values=[
        ["Name", "Email", "Phone"],
        ["John", "john@email.com", "123"],
        ["Jane", "jane@email.com", "456"]
    ]
)
```

### 📊 **Data Management Handlers**

#### 4. `append_data_handler.py`
**Purpose**: Append values to the end of a column
**Function**: `append_data_to_column()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `column_range`: Column range (e.g., 'Sheet1!A:A')
- `values`: List of values to append to the column

**Example**:
```python
result = append_data_to_column(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    column_range="Sheet1!A:A",
    values=["Alice", "Bob", "Charlie"]
)
```

#### 5. `clear_range_handler.py`
**Purpose**: Clear all values from a range
**Function**: `clear_range_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `range`: Range to clear (e.g., 'Sheet1!A1:B10')

**Example**:
```python
result = clear_range_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    range="Sheet1!A1:B10"
)
```

#### 6. `find_replace_handler.py`
**Purpose**: Find and replace text in a range
**Function**: `find_replace_text()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `search_range`: Range to search in (e.g., 'Sheet1!A1:Z100')
- `find_text`: Text to find
- `replace_text`: Text to replace with

**Example**:
```python
result = find_replace_text(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    search_range="Sheet1!A:A",
    find_text="old",
    replace_text="new"
)
```

### 🔧 **Rows & Columns Management Handlers**

#### 7. `insert_rows_handler.py`
**Purpose**: Insert rows in a Google Sheet
**Function**: `insert_rows_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `start_index`: Starting row index (0-based)
- `end_index`: Ending row index (0-based, exclusive)

**Example**:
```python
result = insert_rows_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    start_index=5,
    end_index=8
)
```

#### 8. `delete_rows_handler.py`
**Purpose**: Delete rows from a Google Sheet
**Function**: `delete_rows_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `start_index`: Starting row index (0-based)
- `end_index`: Ending row index (0-based, exclusive)

**Example**:
```python
result = delete_rows_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    start_index=10,
    end_index=13
)
```

#### 9. `insert_columns_handler.py`
**Purpose**: Insert columns in a Google Sheet
**Function**: `insert_columns_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `start_index`: Starting column index (0-based)
- `end_index`: Ending column index (0-based, exclusive)

**Example**:
```python
result = insert_columns_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    start_index=2,
    end_index=5
)
```

#### 10. `delete_columns_handler.py`
**Purpose**: Delete columns from a Google Sheet
**Function**: `delete_columns_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `start_index`: Starting column index (0-based)
- `end_index`: Ending column index (0-based, exclusive)

**Example**:
```python
result = delete_columns_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    start_index=5,
    end_index=8
)
```

#### 11. `move_rows_handler.py`
**Purpose**: Move rows in a Google Sheet
**Function**: `move_rows_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `source_start_index`: Starting row index to move (0-based)
- `source_end_index`: Ending row index to move (0-based, exclusive)
- `destination_index`: Destination row index (0-based)

**Example**:
```python
result = move_rows_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    source_start_index=5,
    source_end_index=8,
    destination_index=15
)
```

#### 12. `resize_columns_handler.py`
**Purpose**: Resize columns in a Google Sheet
**Function**: `resize_columns_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `column_indices`: List of column indices to resize (0-based)
- `widths`: List of widths in pixels for each column

**Example**:
```python
result = resize_columns_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    column_indices=[0, 1, 2],
    widths=[150, 200, 300]
)
```

### 🎨 **Cell Formatting Handlers**

#### 13. `format_cells_handler.py`
**Purpose**: Format cells with colors, fonts, borders, and styling
**Function**: `format_cells_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `start_row_index`: Starting row index (0-based)
- `end_row_index`: Ending row index (0-based, exclusive)
- `start_column_index`: Starting column index (0-based)
- `end_column_index`: Ending column index (0-based, exclusive)
- `background_color`: Background color RGB values (0-1)
- `text_color`: Text color RGB values (0-1)
- `font_family`: Font family name
- `font_size`: Font size in points
- `bold`: Whether text is bold
- `italic`: Whether text is italic
- `underline`: Whether text is underlined
- `horizontal_alignment`: Horizontal alignment
- `vertical_alignment`: Vertical alignment
- `borders`: Border styling

**Example**:
```python
result = format_cells_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    start_row_index=0,
    end_row_index=5,
    start_column_index=0,
    end_column_index=3,
    background_color={'red': 1.0, 'green': 0.5, 'blue': 0.0},
    text_color={'red': 0.0, 'green': 0.0, 'blue': 1.0},
    font_family='Arial',
    font_size=14,
    bold=True
)
```

#### 14. `conditional_format_handler.py`
**Purpose**: Apply conditional formatting with rules-based formatting
**Function**: `conditional_format_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `start_row_index`: Starting row index (0-based)
- `end_row_index`: Ending row index (0-based, exclusive)
- `start_column_index`: Starting column index (0-based)
- `end_column_index`: Ending column index (0-based, exclusive)
- `rule_type`: Type of conditional formatting rule
- `condition_value`: Value to compare against
- `background_color`: Background color RGB values (0-1)
- `text_color`: Text color RGB values (0-1)
- `bold`: Whether text is bold
- `italic`: Whether text is italic

**Example**:
```python
result = conditional_format_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    start_row_index=1,
    end_row_index=10,
    start_column_index=0,
    end_column_index=5,
    rule_type='NUMBER_GREATER_THAN',
    condition_value=100,
    background_color={'red': 1.0, 'green': 0.8, 'blue': 0.8}
)
```

#### 15. `merge_cells_handler.py`
**Purpose**: Merge cells in a Google Sheet
**Function**: `merge_cells_data()`
**Parameters**:
- `spreadsheet_id`: ID of the spreadsheet
- `sheet_id`: ID of the sheet (0-based)
- `start_row_index`: Starting row index (0-based)
- `end_row_index`: Ending row index (0-based, exclusive)
- `start_column_index`: Starting column index (0-based)
- `end_column_index`: Ending column index (0-based, exclusive)
- `merge_type`: Type of merge operation

**Example**:
```python
result = merge_cells_data(
    sheets_service=sheets_service,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    sheet_id=0,
    start_row_index=0,
    end_row_index=2,
    start_column_index=0,
    end_column_index=3,
    merge_type='MERGE_ALL'
)
```

## Benefits of Individual Handlers

### 🎯 **Single Responsibility**
Each handler focuses on one specific operation:
- `write_cell_handler.py` → Write single cell
- `write_row_handler.py` → Write row data
- `write_grid_handler.py` → Write grid data
- `append_data_handler.py` → Append to column
- `clear_range_handler.py` → Clear range
- `find_replace_handler.py` → Find and replace
- `insert_rows_handler.py` → Insert rows
- `delete_rows_handler.py` → Delete rows
- `insert_columns_handler.py` → Insert columns
- `delete_columns_handler.py` → Delete columns
- `move_rows_handler.py` → Move rows
- `resize_columns_handler.py` → Resize columns
- `format_cells_handler.py` → Format cells
- `conditional_format_handler.py` → Conditional formatting
- `merge_cells_handler.py` → Merge cells

### 🔧 **Easy Maintenance**
- Isolated functionality makes debugging easier
- Changes to one handler don't affect others
- Clear separation of concerns
- Simple to test individual functions

### 📚 **Better Documentation**
Each handler includes:
- Clear function documentation
- Parameter descriptions
- Usage examples
- Error handling

### 🚀 **Improved Performance**
- No unnecessary function calls
- Direct API interactions
- Optimized for specific use cases
- Reduced complexity

## Handler Structure Pattern

Each handler follows a consistent pattern:

```python
# 1. Imports
from typing import Any, Dict
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

# 2. Request/Response Models
class HandlerRequest(BaseModel):
    """Request model for the operation."""
    # ... field definitions

class HandlerResponse(BaseModel):
    """Response model for the operation."""
    # ... field definitions

# 3. Main Function
def handler_function(
    sheets_service,
    spreadsheet_id: str,
    # ... other parameters
) -> Dict[str, Any]:
    """
    Clear documentation of what the function does.
    
    Args:
        # ... parameter descriptions
    
    Returns:
        # ... return value description
    """
    
    try:
        # API call implementation
        # ... Google Sheets API calls
        
        return {
            # ... structured response
        }
        
    except HttpError as error:
        # Error handling
        raise RuntimeError(f"Error message: {error_message}")
    except Exception as error:
        # General error handling
        raise RuntimeError(f"Unexpected error: {error}")
```

## Integration with Main Server

The main server file (`fastmcp_server_simple.py`) now imports and uses these handlers:

```python
# Import individual handlers
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

# Use handlers in tool functions
@mcp.tool()
def write_cell(spreadsheet_id: str, cell: str, value: str) -> Dict[str, Any]:
    return write_cell_data(
        sheets_service=sheets_service,
        spreadsheet_id=spreadsheet_id,
        cell=cell,
        value=value
    )
```

## Migration from Complex Handler

The original `write_sheet_data_handler.py` contained multiple functions:
- `write_multiple_ranges()`
- `write_sheet_data_with_ranges_and_values()`
- `clear_sheet_data()`
- `append_sheet_data()`

These have been replaced with individual handlers that are:
- **Simpler**: Each handles one specific operation
- **Clearer**: Direct parameter mapping
- **More maintainable**: Isolated functionality
- **Better documented**: Specific examples and use cases

## Next Steps

1. **Testing**: Each handler can be tested independently
2. **Documentation**: Add more specific examples for each handler
3. **Error Handling**: Enhance error messages for specific use cases
4. **Performance**: Optimize each handler for its specific operation
5. **Validation**: Add input validation specific to each operation

This modular approach makes the codebase much more maintainable and easier for AI hosts to understand and use effectively. 