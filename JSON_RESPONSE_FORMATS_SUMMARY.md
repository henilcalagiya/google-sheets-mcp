# JSON Response Formats - Tool Summary

## Overview
This document summarizes which tools in the Google Sheets MCP server use **compact JSON responses** (string format) vs **regular Dict responses** (Python dictionary format).

## ✅ **Compact JSON Response Tools (Returns `str`)**

### **🔍 Metadata Tools:**
1. **`get_sheet_metadata_tool`** → `str`
   - **Purpose**: Get detailed metadata for a specific sheet
   - **Format**: Compact JSON string with no newlines
   - **Reason**: Large metadata objects with many nested structures

2. **`get_spreadsheet_metadata_tool`** → `str`
   - **Purpose**: Get basic spreadsheet metadata
   - **Format**: Compact JSON string with no newlines
   - **Reason**: Spreadsheet-level metadata with nested objects

### **📊 Implementation Details:**
```python
# These tools use compact_json_response() in their handlers
return compact_json_response({
    "success": True,
    "spreadsheet_name": "My Spreadsheet",
    "sheet_name": "Sheet1",
    "metadata": {...}
})
```

### **🎯 Benefits of Compact JSON:**
- **Reduced Character Count**: No newlines or extra spaces
- **AI Host Compatibility**: Better for 2000-word limits
- **Efficient Serialization**: Uses `json.dumps(data, separators=(',', ':'))`
- **Consistent Format**: All metadata tools use the same approach

## ✅ **Regular Dict Response Tools (Returns `Dict[str, Any]`)**

### **📋 List/Overview Tools:**
1. **`get_all_spreadsheets_overview_tool`** → `Dict[str, Any]`
2. **`list_all_spreadsheets`** → `Dict[str, Any]`
3. **`list_sheets_tool`** → `Dict[str, Any]`

### **✏️ Edit/Modify Tools:**
4. **`rename_spreadsheet_tool`** → `Dict[str, Any]`
5. **`add_sheets_tool`** → `Dict[str, Any]`
6. **`delete_sheets_tool`** → `Dict[str, Any]`
7. **`duplicate_sheet_tool`** → `Dict[str, Any]`
8. **`rename_sheets_tool`** → `Dict[str, Any]`

### **📖 Read/Data Tools:**
9. **`read_sheet_data_tool`** → `Dict[str, Any]`
10. **`find_replace`** → `Dict[str, Any]`

### **🔧 Dimension/Structure Tools:**
11. **`insert_sheet_dimension`** → `Dict[str, Any]`
12. **`delete_sheet_dimension`** → `Dict[str, Any]`
13. **`move_sheet_dimension`** → `Dict[str, Any]`
14. **`resize_columns`** → `Dict[str, Any]`

### **📊 Chart Tools:**
15. **`create_chart_tool`** → `Dict[str, Any]`

### **📋 Table Tools:**
16. **`add_table_tool`** → `Dict[str, Any]`
17. **`delete_table_tool`** → `Dict[str, Any]`
18. **`add_table_records_tool`** → `Dict[str, Any]`
19. **`modify_table_ranges_tool`** → `REMOVED`

### **🎨 Formatting Tools:**
20. **`format_cells_handler`** → `Dict[str, Any]`
21. **`merge_cells_handler`** → `Dict[str, Any]`

## 📊 **Comparison Table**

| Tool Category | Tool Name | Return Type | Format | Reason |
|---------------|-----------|-------------|---------|---------|
| **Metadata** | `get_sheet_metadata_tool` | `str` | Compact JSON | Large nested objects |
| **Metadata** | `get_spreadsheet_metadata_tool` | `str` | Compact JSON | Large nested objects |
| **List** | `list_all_spreadsheets` | `Dict[str, Any]` | Regular Dict | Simple lists |
| **List** | `list_sheets_tool` | `Dict[str, Any]` | Regular Dict | Simple lists |
| **Edit** | `add_sheets_tool` | `Dict[str, Any]` | Regular Dict | Simple success/failure |
| **Edit** | `delete_sheets_tool` | `Dict[str, Any]` | Regular Dict | Simple success/failure |
| **Data** | `read_sheet_data_tool` | `Dict[str, Any]` | Regular Dict | Cell data arrays |
| **Charts** | `create_chart_tool` | `Dict[str, Any]` | Regular Dict | Chart configuration |
| **Tables** | `add_table_tool` | `Dict[str, Any]` | Regular Dict | Table creation info |

## 🔧 **Technical Implementation**

### **Compact JSON Tools:**
```python
# Handler returns compact JSON string
def get_sheet_metadata_handler(...) -> str:
    return compact_json_response({
        "success": True,
        "metadata": {...}
    })

# Server tool returns string
def get_sheet_metadata_tool(...) -> str:
    return get_sheet_metadata_handler(...)
```

### **Regular Dict Tools:**
```python
# Handler returns Python dict
def list_sheets_handler(...) -> Dict[str, Any]:
    return {
        "success": True,
        "sheets": [...]
    }

# Server tool returns dict
def list_sheets_tool(...) -> Dict[str, Any]:
    return list_sheets_handler(...)
```

## 🎯 **Decision Criteria**

### **✅ Use Compact JSON When:**
- **Large nested objects** (metadata with charts, tables, slicers)
- **Many newlines** in the response
- **AI host compatibility** is critical
- **Character count** needs to be minimized

### **✅ Use Regular Dict When:**
- **Simple success/failure** responses
- **Small data structures** (lists, simple objects)
- **Readability** is important
- **Standard FastMCP** compatibility

## 📈 **Response Examples**

### **Compact JSON Example:**
```json
{"success":true,"spreadsheet_name":"My Spreadsheet","sheet_name":"Sheet1","metadata":{"sheet_id":0,"title":"Sheet1","charts":{"total_charts":2,"chart_types":["BAR","PIE"]},"tables":{"total_tables":1,"table_names":["SalesData"]}}}
```

### **Regular Dict Example:**
```json
{
  "success": true,
  "spreadsheet_name": "My Spreadsheet",
  "sheets": [
    {
      "title": "Sheet1",
      "index": 0
    }
  ],
  "total_sheets": 1
}
```

## ✅ **Summary**

### **🔍 Compact JSON Tools (2):**
- `get_sheet_metadata_tool` - Detailed sheet metadata
- `get_spreadsheet_metadata_tool` - Basic spreadsheet metadata

### **📋 Regular Dict Tools (21+):**
- All other tools use standard `Dict[str, Any]` returns
- Simple, readable responses
- Standard FastMCP compatibility

**The choice is based on response complexity and AI host compatibility needs!** 🎯 