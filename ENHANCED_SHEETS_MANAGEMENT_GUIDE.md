# 🚀 Enhanced Sheets Management Tool Guide

## 🎯 **Overview**

The **Enhanced Sheets Management Tool** combines sheet management operations (add/delete/list) with detailed metadata functionality in a single, powerful tool.

## 📋 **Key Features**

### **✅ Sheet Management Operations**
- List all sheets with basic info
- Add new sheets to spreadsheet
- Delete existing sheets from spreadsheet
- Track operation results

### **✅ Metadata Integration**
- Include detailed metadata (optional)
- Focus on specific sheet metadata
- Performance control (fast vs detailed)
- Error handling for metadata retrieval

### **✅ Flexible Usage**
- Single tool for multiple operations
- Configurable metadata inclusion
- Focused queries for efficiency

---

## 🛠️ **Tool Parameters**

```python
@mcp.tool()
def enhanced_sheets_management_tool(
    spreadsheet_id: str,                    # Required: Spreadsheet ID
    add_sheet_names: List[str] = [],        # Optional: Sheet names to add
    delete_sheet_ids: List[int] = [],       # Optional: Sheet IDs to delete
    include_metadata: bool = True,          # Optional: Include metadata
    target_sheet_name: str = None           # Optional: Focus on specific sheet
) -> Dict[str, Any]:
```

### **📥 Input Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spreadsheet_id` | `str` | ✅ | The Google Spreadsheet ID |
| `add_sheet_names` | `List[str]` | ❌ | List of sheet names to add |
| `delete_sheet_ids` | `List[int]` | ❌ | List of sheet IDs to delete |
| `include_metadata` | `bool` | ❌ | Include detailed metadata (default: True) |
| `target_sheet_name` | `str` | ❌ | Focus metadata on specific sheet |

---

## 📤 **Output Structure**

```python
{
    # Basic sheet management info
    "sheets": [
        {
            "sheet_id": 123,
            "title": "Sheet1",
            "index": 0,
            "grid_properties": {"rowCount": 1000, "columnCount": 26}
        }
    ],
    
    # Operation results
    "added": [
        {
            "sheet_id": 456,
            "title": "NewSheet",
            "index": 5,
            "grid_properties": {"rowCount": 1000, "columnCount": 26}
        }
    ],
    "deleted": [789],
    
    # Detailed metadata (if include_metadata=True)
    "metadata": {
        "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
        "total_sheets": 5,
        "sheets": [
            {
                "sheet_id": 123,
                "title": "Sheet1",
                "index": 0,
                "grid_properties": {"rowCount": 1000, "columnCount": 26},
                "hidden": False,
                "tab_color": {"red": 1.0, "green": 0.0, "blue": 0.0},
                "protected_ranges": [...],
                "basic_filter": {...}
            }
        ]
    },
    
    # Summary and tracking
    "message": "Added 1 sheet(s), Deleted 1 sheet(s). Listed sheets with metadata.",
    "operations_performed": {
        "sheets_added": 1,
        "sheets_deleted": 1,
        "metadata_included": True
    }
}
```

---

## 🎯 **Usage Examples**

### **1. Basic Operation (Fast)**
```python
# List all sheets without metadata
result = enhanced_sheets_management_tool(
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    include_metadata=False
)
```

### **2. All Sheets with Metadata**
```python
# List all sheets with detailed metadata
result = enhanced_sheets_management_tool(
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    include_metadata=True
)
```

### **3. Focus on Specific Sheet**
```python
# Get metadata for specific sheet only
result = enhanced_sheets_management_tool(
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    include_metadata=True,
    target_sheet_name="Sheet1"
)
```

### **4. Add Sheets with Metadata**
```python
# Add new sheets and get metadata
result = enhanced_sheets_management_tool(
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    add_sheet_names=["NewSheet1", "NewSheet2"],
    include_metadata=True
)
```

### **5. Delete Sheets with Metadata**
```python
# Delete sheets and get metadata
result = enhanced_sheets_management_tool(
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    delete_sheet_ids=[123, 456],
    include_metadata=True
)
```

### **6. Complex Operation**
```python
# Add sheets, focus on specific sheet metadata
result = enhanced_sheets_management_tool(
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    add_sheet_names=["DataSheet"],
    include_metadata=True,
    target_sheet_name="Summary"
)
```

---

## ⚡ **Performance Options**

### **🚀 Fast Mode**
```python
include_metadata=False
```
- **Use when**: You need quick sheet list
- **Performance**: Fastest response
- **Data**: Basic sheet info only

### **📊 Full Metadata Mode**
```python
include_metadata=True, target_sheet_name=None
```
- **Use when**: You need complete sheet details
- **Performance**: Standard response
- **Data**: All sheets with full metadata

### **🎯 Focused Mode**
```python
include_metadata=True, target_sheet_name="SheetName"
```
- **Use when**: You need details for specific sheet
- **Performance**: Optimized response
- **Data**: All sheets basic + specific sheet detailed

---

## 🔍 **Metadata Details**

### **Basic Sheet Info (Always Included)**
```python
{
    "sheet_id": 123,
    "title": "Sheet1",
    "index": 0,
    "grid_properties": {"rowCount": 1000, "columnCount": 26}
}
```

### **Detailed Metadata (When include_metadata=True)**
```python
{
    "sheet_id": 123,
    "title": "Sheet1",
    "index": 0,
    "grid_properties": {"rowCount": 1000, "columnCount": 26},
    "hidden": False,
    "tab_color": {"red": 1.0, "green": 0.0, "blue": 0.0},
    "protected_ranges": [...],
    "basic_filter": {...},
    "conditional_formats": [...],
    "data_validation": [...]
}
```

---

## 🎯 **When to Use Each Mode**

### **Use Fast Mode When:**
- ✅ Quick sheet listing needed
- ✅ Performance is critical
- ✅ Basic info is sufficient
- ✅ High-frequency operations

### **Use Full Metadata When:**
- ✅ Complete sheet analysis needed
- ✅ Understanding sheet structure
- ✅ Planning complex operations
- ✅ Debugging sheet issues

### **Use Focused Mode When:**
- ✅ Specific sheet analysis
- ✅ Targeted operations
- ✅ Optimizing performance
- ✅ Detailed sheet inspection

---

## 🚀 **Benefits Over Separate Tools**

### **✅ Efficiency**
- Single API call instead of multiple
- Reduced tool complexity
- Unified data structure

### **✅ Context**
- Operations + metadata in one response
- Better decision-making
- Complete picture of changes

### **✅ Flexibility**
- Configurable metadata inclusion
- Focused queries
- Performance optimization

### **✅ Error Handling**
- Graceful metadata failure handling
- Operation tracking
- Detailed error messages

---

## 🔧 **Error Handling**

The tool includes robust error handling:

```python
# Metadata retrieval failure
{
    "sheets": [...],
    "metadata_error": "Error message",
    "message": "Listed sheets. (metadata retrieval failed)"
}

# Successful operation
{
    "sheets": [...],
    "metadata": {...},
    "message": "Added 1 sheet(s). Listed sheets with metadata."
}
```

---

## 📋 **Migration from Old Tools**

### **Old Way (Multiple Tools)**
```python
# 1. Get sheet list
sheets = sheets_management_tool(spreadsheet_id="123")

# 2. Get metadata separately
metadata = sheet_management_tool(spreadsheet_id="123", include_metadata=True)
```

### **New Way (Single Tool)**
```python
# Combined operation
result = enhanced_sheets_management_tool(
    spreadsheet_id="123",
    include_metadata=True
)
```

This enhanced tool provides **maximum functionality** with **optimal performance** options! 🚀 