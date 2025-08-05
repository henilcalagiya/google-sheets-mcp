# Google Sheets API v4 - Table Objects Reference

## 📋 Overview

This document provides a comprehensive reference for all table-related objects in the Google Sheets API v4. Tables are structured data collections that provide automatic formatting, filtering, and data management capabilities.

## 🏗️ Core Table Objects

### 1. Table Object
The main table object that represents a table in Google Sheets.

```json
{
  "tableId": 1,
  "displayName": "Project Tracker",
  "range": {
    "sheetId": 0,
    "startRowIndex": 0,
    "endRowIndex": 10,
    "startColumnIndex": 0,
    "endColumnIndex": 5
  },
  "columnCount": 5,
  "rows": [...],
  "columns": [...],
  "style": {...}
}
```

**Properties:**
- `tableId` (integer): The ID of the table
- `displayName` (string): The display name of the table
- `range` (GridRange): The range the table covers
- `columnCount` (integer): The number of columns in the table
- `rows` (array): The rows in the table
- `columns` (array): The columns in the table
- `style` (TableStyle): The style of the table

### 2. TableRow Object
Represents a row in a table.

```json
{
  "values": [
    {"userEnteredValue": {"stringValue": "John"}},
    {"userEnteredValue": {"numberValue": 25}},
    {"userEnteredValue": {"stringValue": "New York"}}
  ]
}
```

**Properties:**
- `values` (array): The values in the row

### 3. TableColumn Object
Represents a column in a table.

```json
{
  "columnId": "col_1",
  "displayName": "Name",
  "index": 0
}
```

**Properties:**
- `columnId` (string): The ID of the column
- `displayName` (string): The display name of the column
- `index` (integer): The index of the column

### 4. TableStyle Object
Defines the visual style of a table.

```json
{
  "headerRow": true,
  "totalRow": false,
  "firstColumn": false,
  "lastColumn": false,
  "bandedRows": true,
  "bandedColumns": false
}
```

**Properties:**
- `headerRow` (boolean): True if the header row should be shown
- `totalRow` (boolean): True if the total row should be shown
- `firstColumn` (boolean): True if the first column should be shown
- `lastColumn` (boolean): True if the last column should be shown
- `bandedRows` (boolean): True if the rows should be banded
- `bandedColumns` (boolean): True if the columns should be banded

## 📊 Column Properties Objects

### 5. TableColumnProperties Object
Defines properties for table columns.

```json
{
  "columnId": "col_1",
  "displayName": "Task Name"
}
```

**Properties:**
- `columnId` (string): The column ID
- `displayName` (string): The display name

### 6. TableColumnDataValidationRule Object
Defines data validation rules for table columns.

```json
{
  "condition": {
    "type": "ONE_OF_LIST",
    "values": [
      {"userEnteredValue": "Not Started"},
      {"userEnteredValue": "In Progress"},
      {"userEnteredValue": "Complete"}
    ]
  },
  "showCustomUi": true,
  "strict": true
}
```

**Properties:**
- `condition` (BooleanCondition): The condition that data must match
- `showCustomUi` (boolean): True if custom UI should be shown
- `strict` (boolean): True if strict validation should be enforced

### 7. TableRowsProperties Object
Defines properties for table rows.

```json
{
  "headerRow": true,
  "totalRow": false
}
```

**Properties:**
- `headerRow` (boolean): True if header row should be shown
- `totalRow` (boolean): True if total row should be shown

## 🔧 Request Objects

### 8. AddTableRequest Object
Request to add a new table.

```json
{
  "addTable": {
    "table": {
      "name": "Project Tracker",
      "tableId": "table_project_tracker",
      "range": {
        "sheetId": 0,
        "startColumnIndex": 0,
        "endColumnIndex": 5,
        "startRowIndex": 0,
        "endRowIndex": 5
      },
      "columnProperties": [
        {
          "columnIndex": 0,
          "columnName": "Task",
          "columnType": "TEXT"
        },
        {
          "columnIndex": 1,
          "columnName": "Status",
          "columnType": "DROPDOWN",
          "dataValidationRule": {
            "condition": {
              "type": "ONE_OF_LIST",
              "values": [
                {"userEnteredValue": "Not Started"},
                {"userEnteredValue": "In Progress"},
                {"userEnteredValue": "Complete"}
              ]
            }
          }
        }
      ]
    }
  }
}
```

**Properties:**
- `table` (Table): The table to add

### 9. AddTableResponse Object
Response when adding a table.

```json
{
  "addTable": {
    "table": {
      "tableId": "table_project_tracker",
      "displayName": "Project Tracker",
      "range": {
        "sheetId": 0,
        "startRowIndex": 0,
        "endRowIndex": 5,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      },
      "columnCount": 5,
      "rows": [...],
      "columns": [...]
    }
  }
}
```

**Properties:**
- `table` (Table): The table that was added

### 10. DeleteTableRequest Object
Request to delete a table.

```json
{
  "deleteTable": {
    "tableId": "table_project_tracker"
  }
}
```

**Properties:**
- `tableId` (integer): The ID of the table to delete

### 11. UpdateTableRequest Object
Request to update a table.

```json
{
  "updateTable": {
    "table": {
      "tableId": "table_project_tracker",
      "displayName": "Updated Project Tracker",
      "range": {
        "sheetId": 0,
        "startRowIndex": 0,
        "endRowIndex": 15,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      }
    },
    "fields": "displayName,range"
  }
}
```

**Properties:**
- `table` (Table): The table to update
- `fields` (string): The fields to update

### 12. AppendCellsRequest Object
Request to append cells to a table.

```json
{
  "appendCells": {
    "sheetId": 0,
    "tableId": "table_project_tracker",
    "rows": [
      {
        "values": [
          {"userEnteredValue": {"stringValue": "Design UI"}},
          {"userEnteredValue": {"stringValue": "In Progress"}},
          {"userEnteredValue": {"numberValue": 0.75}},
          {"userEnteredValue": {"numberValue": 44562}},
          {"userEnteredValue": {"stringValue": "High"}}
        ]
      }
    ],
    "fields": "userEnteredValue,userEnteredFormat"
  }
}
```

**Properties:**
- `sheetId` (integer): The sheet to append cells to
- `tableId` (integer): The table ID
- `rows` (array): The rows to append
- `fields` (string): The fields to update

## 📝 Column Type Objects

### 13. Column Properties for Different Types

#### Text Column
```json
{
  "columnIndex": 0,
  "columnName": "Name",
  "columnType": "TEXT"
}
```

#### Number Column
```json
{
  "columnIndex": 1,
  "columnName": "Age",
  "columnType": "DOUBLE"
}
```

#### Date Column
```json
{
  "columnIndex": 2,
  "columnName": "Birth Date",
  "columnType": "DATE"
}
```

#### Percent Column
```json
{
  "columnIndex": 3,
  "columnName": "Completion",
  "columnType": "PERCENT"
}
```

#### Currency Column
```json
{
  "columnIndex": 4,
  "columnName": "Price",
  "columnType": "CURRENCY"
}
```

#### Time Column
```json
{
  "columnIndex": 5,
  "columnName": "Start Time",
  "columnType": "TIME"
}
```

#### DateTime Column
```json
{
  "columnIndex": 6,
  "columnName": "Created",
  "columnType": "DATE_TIME"
}
```

#### Dropdown Column
```json
{
  "columnIndex": 7,
  "columnName": "Status",
  "columnType": "DROPDOWN",
  "dataValidationRule": {
    "condition": {
      "type": "ONE_OF_LIST",
      "values": [
        {"userEnteredValue": "Not Started"},
        {"userEnteredValue": "In Progress"},
        {"userEnteredValue": "Complete"}
      ]
    }
  }
}
```

#### Checkbox Column
```json
{
  "columnIndex": 8,
  "columnName": "Done",
  "columnType": "CHECKBOX"
}
```

#### Smart Chip Column
```json
{
  "columnIndex": 9,
  "columnName": "Assignee",
  "columnType": "SMART_CHIP"
}
```

## 🔄 Data Validation Objects

### 14. BooleanCondition Object
Defines conditions for data validation.

```json
{
  "type": "ONE_OF_LIST",
  "values": [
    {"userEnteredValue": "Option 1"},
    {"userEnteredValue": "Option 2"},
    {"userEnteredValue": "Option 3"}
  ]
}
```

**Properties:**
- `type` (string): The type of condition
- `values` (array): The values for the condition

### 15. DataValidationRule Object
Complete data validation rule for table columns.

```json
{
  "condition": {
    "type": "ONE_OF_LIST",
    "values": [
      {"userEnteredValue": "Low"},
      {"userEnteredValue": "Medium"},
      {"userEnteredValue": "High"}
    ]
  },
  "showCustomUi": true,
  "strict": true,
  "inputMessage": "Please select a priority level",
  "errorMessage": "Invalid priority level"
}
```

**Properties:**
- `condition` (BooleanCondition): The condition that data must match
- `showCustomUi` (boolean): True if custom UI should be shown
- `strict` (boolean): True if strict validation should be enforced
- `inputMessage` (string): Message shown when adding data to cell
- `errorMessage` (string): Message shown when validation fails

## 📊 Cell Value Objects

### 16. CellData Object
Represents cell data in table rows.

```json
{
  "userEnteredValue": {
    "stringValue": "Task Name"
  },
  "userEnteredFormat": {
    "numberFormat": {
      "type": "TEXT"
    }
  }
}
```

**Properties:**
- `userEnteredValue` (ExtendedValue): The value entered by the user
- `userEnteredFormat` (CellFormat): The format of the cell

### 17. ExtendedValue Object
Represents different types of cell values.

```json
// String value
{"stringValue": "Hello World"}

// Number value
{"numberValue": 42.5}

// Boolean value
{"boolValue": true}

// Formula value
{"formulaValue": "=SUM(A1:A10)"}

// Error value
{"errorValue": {"type": "DIVIDE_BY_ZERO"}}
```

**Properties:**
- `stringValue` (string): String value
- `numberValue` (number): Numeric value
- `boolValue` (boolean): Boolean value
- `formulaValue` (string): Formula value
- `errorValue` (ErrorValue): Error value

## 🎨 Formatting Objects

### 18. CellFormat Object
Defines cell formatting.

```json
{
  "numberFormat": {
    "type": "PERCENT",
    "pattern": "0.00%"
  },
  "backgroundColor": {
    "red": 0.9,
    "green": 0.9,
    "blue": 0.9
  },
  "textFormat": {
    "bold": true,
    "fontSize": 12
  }
}
```

**Properties:**
- `numberFormat` (NumberFormat): Number formatting
- `backgroundColor` (Color): Background color
- `textFormat` (TextFormat): Text formatting

### 19. NumberFormat Object
Defines number formatting for table columns.

```json
{
  "type": "CURRENCY",
  "pattern": "$#,##0.00"
}
```

**Properties:**
- `type` (string): The type of number format
- `pattern` (string): The pattern for formatting

### 20. Color Object
Represents colors in table formatting.

```json
{
  "red": 1.0,
  "green": 0.5,
  "blue": 0.0,
  "alpha": 1.0
}
```

**Properties:**
- `red` (number): Red component (0.0 to 1.0)
- `green` (number): Green component (0.0 to 1.0)
- `blue` (number): Blue component (0.0 to 1.0)
- `alpha` (number): Alpha component (0.0 to 1.0)

## 📋 Summary

### **Total Table-Related Objects: 20**

**Core Objects (4):**
1. Table
2. TableRow
3. TableColumn
4. TableStyle

**Column Properties (3):**
5. TableColumnProperties
6. TableColumnDataValidationRule
7. TableRowsProperties

**Request Objects (4):**
8. AddTableRequest
9. AddTableResponse
10. DeleteTableRequest
11. UpdateTableRequest
12. AppendCellsRequest

**Column Types (9):**
13. Text Column
14. Number Column
15. Date Column
16. Percent Column
17. Currency Column
18. Time Column
19. DateTime Column
20. Dropdown Column
21. Checkbox Column
22. Smart Chip Column

**Data Validation (2):**
23. BooleanCondition
24. DataValidationRule

**Cell Values (2):**
25. CellData
26. ExtendedValue

**Formatting (3):**
27. CellFormat
28. NumberFormat
29. Color

## 🔗 Related Documentation

- **[API Overview](01_API_Overview.md)** - Basic API information
- **[Tables Reference](14_Tables_Reference.md)** - Table operations and examples
- **[Batch Operations](04_Batch_Operations.md)** - Batch update request types
- **[Schemas Reference](03_Schemas_Reference.md)** - Complete schema definitions

---

*This documentation covers all table-related objects in Google Sheets API v4.* 