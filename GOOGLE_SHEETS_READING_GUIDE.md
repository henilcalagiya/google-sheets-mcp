# 📊 Google Sheets Reading Guide - 3 Reading Options

## 🎯 **Overview**

The Google Sheets API provides **3 main reading patterns** for accessing data:

1. **Column-wise Reading** - Read entire columns or column ranges
2. **Row-wise Reading** - Read entire rows or row ranges  
3. **Custom Range Reading** - Read specific ranges from single cells to entire sheets

## 📋 **1. Column-wise Reading**

### **Purpose**
Read data vertically (down columns) - useful for:
- Reading lists of data
- Extracting specific fields (e.g., all names, all emails)
- Processing columnar data

### **API Endpoint**
```
GET /v4/spreadsheets/{spreadsheetId}/values/{sheetName}!{columnRange}
```

### **Examples**

#### **Read Entire Column**
```python
# Read all data in column A
read_type = "column"
range_spec = "A"
# Results in: Sheet1!A:A
```

#### **Read Column Range**
```python
# Read column A from row 1 to 100
read_type = "column" 
range_spec = "A1:A100"
# Results in: Sheet1!A1:A100
```

#### **Read Multiple Columns**
```python
# Read columns A, B, C
ranges = ["Sheet1!A:A", "Sheet1!B:B", "Sheet1!C:C"]
```

### **Use Cases**
- ✅ Reading contact lists (names, emails, phones)
- ✅ Processing survey responses
- ✅ Extracting specific data fields
- ✅ Reading time-series data

---

## 📋 **2. Row-wise Reading**

### **Purpose**
Read data horizontally (across rows) - useful for:
- Reading complete records
- Processing row-based data
- Reading headers and data rows

### **API Endpoint**
```
GET /v4/spreadsheets/{spreadsheetId}/values/{sheetName}!{rowRange}
```

### **Examples**

#### **Read Entire Row**
```python
# Read all data in row 1
read_type = "row"
range_spec = "1"
# Results in: Sheet1!1:1
```

#### **Read Row Range**
```python
# Read rows 1 to 10
read_type = "row"
range_spec = "1:10"
# Results in: Sheet1!1:10
```

#### **Read Header Row**
```python
# Read just the header row
read_type = "row"
range_spec = "1"
```

### **Use Cases**
- ✅ Reading complete records (all fields for a person)
- ✅ Processing tabular data
- ✅ Reading headers and data rows
- ✅ Analyzing row-based patterns

---

## 📋 **3. Custom Range Reading**

### **Purpose**
Read specific rectangular ranges - most flexible option for:
- Reading specific data blocks
- Reading single cells
- Reading large areas efficiently

### **API Endpoint**
```
GET /v4/spreadsheets/{spreadsheetId}/values/{sheetName}!{customRange}
```

### **Examples**

#### **Read Single Cell**
```python
# Read cell A1
read_type = "custom"
range_spec = "A1"
# Results in: Sheet1!A1
```

#### **Read Specific Range**
```python
# Read range A1 to B10
read_type = "custom"
range_spec = "A1:B10"
# Results in: Sheet1!A1:B10
```

#### **Read Large Area**
```python
# Read large area A1 to Z1000
read_type = "custom"
range_spec = "A1:Z1000"
# Results in: Sheet1!A1:Z1000
```

#### **Read Entire Sheet**
```python
# Read all data in sheet
read_type = "custom"
range_spec = "A:Z"  # or just leave empty for entire sheet
# Results in: Sheet1
```

### **Use Cases**
- ✅ Reading specific data blocks
- ✅ Reading single values (cell references)
- ✅ Reading large datasets efficiently
- ✅ Reading irregular data shapes

---

## 🛠️ **Implementation Examples**

### **MCP Tool Usage**

```python
# Single or multiple ranges reading
@mcp.tool()
def read_multiple_ranges_tool(
    spreadsheet_id: str,
    ranges: List[str],  # ["Sheet1!A:A", "Sheet1!B:B", "Sheet2!A1:B10"]
    value_render_option: str = "FORMATTED_VALUE"
) -> Dict[str, Any]:
    """
    Read single or multiple ranges efficiently:
    - Single column: ["Sheet1!A:A"]
    - Multiple columns: ["Sheet1!A:A", "Sheet1!B:B", "Sheet1!C:C"]
    - Custom ranges: ["Sheet1!A1:B10", "Sheet2!A1:D5"]
    """
```

### **Function Calls**

```python
# Single range examples
read_multiple_ranges(sheets_service, "spreadsheet_id", ["Sheet1!A:A"])
read_multiple_ranges(sheets_service, "spreadsheet_id", ["Sheet1!1:1"])
read_multiple_ranges(sheets_service, "spreadsheet_id", ["Sheet1!A1:B10"])

# Multiple ranges examples
ranges = ["Sheet1!A1:A10", "Sheet1!B1:B10", "Sheet2!A:A"]
result = read_multiple_ranges(sheets_service, "spreadsheet_id", ranges)

# Cross-sheet examples
ranges = ["Sheet1!A:A", "Sheet2!B:B", "Sheet3!A1:D10"]
result = read_multiple_ranges(sheets_service, "spreadsheet_id", ranges)
```

---

## 📊 **Performance Comparison**

| Reading Type | Best For | API Calls | Performance |
|--------------|----------|-----------|-------------|
| **Column-wise** | Vertical data, lists | 1 per column | ⭐⭐⭐⭐ |
| **Row-wise** | Horizontal data, records | 1 per row range | ⭐⭐⭐⭐ |
| **Custom Range** | Specific blocks, cells | 1 per range | ⭐⭐⭐⭐⭐ |

---

## 🎯 **When to Use Each Option**

### **Use Column-wise When:**
- ✅ You need all values from a specific field
- ✅ Processing list data (names, emails, IDs)
- ✅ Reading time-series data
- ✅ Extracting specific data columns

### **Use Row-wise When:**
- ✅ You need complete records
- ✅ Reading headers and data rows
- ✅ Processing tabular data
- ✅ Analyzing row patterns

### **Use Custom Range When:**
- ✅ You need specific data blocks
- ✅ Reading single cells or small ranges
- ✅ Reading irregular data shapes
- ✅ Maximum flexibility needed

---

## 🔧 **Advanced Features**

### **Value Rendering Options**
```python
value_render_option = "FORMATTED_VALUE"    # Human-readable values
value_render_option = "UNFORMATTED_VALUE"  # Raw values
value_render_option = "FORMULA"            # Cell formulas
```

### **Date Time Rendering**
```python
date_time_render_option = "FORMATTED_STRING"  # Human-readable dates
date_time_render_option = "SERIAL_NUMBER"     # Excel date numbers
```

### **Multiple Ranges (Batch Reading)**
```python
ranges = [
    "Sheet1!A1:A10",
    "Sheet1!B1:B10", 
    "Sheet2!A1:A5"
]
result = read_multiple_ranges(sheets_service, spreadsheet_id, ranges)
```

---

## 🚀 **Quick Reference**

### **Column Reading**
```python
# Entire column
range_spec = "A"      # Column A
range_spec = "B"      # Column B

# Column range
range_spec = "A1:A100"  # A1 to A100
range_spec = "B5:B50"   # B5 to B50
```

### **Row Reading**
```python
# Entire row
range_spec = "1"      # Row 1
range_spec = "5"      # Row 5

# Row range
range_spec = "1:10"   # Rows 1 to 10
range_spec = "5:15"   # Rows 5 to 15
```

### **Custom Range**
```python
# Single cell
range_spec = "A1"     # Cell A1
range_spec = "B5"     # Cell B5

# Specific range
range_spec = "A1:B10" # A1 to B10
range_spec = "C5:F20" # C5 to F20

# Large range
range_spec = "A1:Z1000" # A1 to Z1000
```

This comprehensive guide covers all three reading options with practical examples and use cases for the Google Sheets API! 