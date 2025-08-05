# Google Sheets API v4 - Tables Reference

## 📋 Overview

This document provides a comprehensive reference for working with tables in Google Sheets API v4. Tables are structured data collections that simplify data creation and management by automatically applying format and structure to ranges of data.

## 🎯 What is a Table?

Tables in Google Sheets are structured data collections that provide:
- **Headers**: Column names and formatting
- **Footers**: Optional summary rows
- **Column Types**: Different data types (TEXT, DOUBLE, DATE, PERCENT, DROPDOWN, etc.)
- **Filters**: Built-in filtering capabilities
- **Views**: Multiple ways to view the same data
- **Table References**: Named references for formulas
- **Table Names**: Identifiable names for easy reference

## 📊 Table Schema

### Table Object
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

### TableRow Object
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

### TableColumn Object
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

### TableStyle Object
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

### TableColumnProperties Object
```json
{
  "columnId": "col_1",
  "displayName": "Task Name"
}
```

**Properties:**
- `columnId` (string): The column ID
- `displayName` (string): The display name

### TableColumnDataValidationRule Object
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

### TableRowsProperties Object
```json
{
  "headerRow": true,
  "totalRow": false
}
```

**Properties:**
- `headerRow` (boolean): True if header row should be shown
- `totalRow` (boolean): True if total row should be shown

## 🔧 Table Operations

### 1. Add Table (addTable)

Creates a new table in a spreadsheet.

**Request Type:** AddTableRequest
**Request:**
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
        },
        {
          "columnIndex": 2,
          "columnName": "Progress",
          "columnType": "PERCENT"
        },
        {
          "columnIndex": 3,
          "columnName": "Due Date",
          "columnType": "DATE"
        },
        {
          "columnIndex": 4,
          "columnName": "Priority",
          "columnType": "DROPDOWN",
          "dataValidationRule": {
            "condition": {
              "type": "ONE_OF_LIST",
              "values": [
                {"userEnteredValue": "Low"},
                {"userEnteredValue": "Medium"},
                {"userEnteredValue": "High"}
              ]
            }
          }
        }
      ]
    }
  }
}
```

**Response Type:** AddTableResponse
**Response:**
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
      "rows": [
        {
          "values": [
            {"userEnteredValue": {"stringValue": "Task"}},
            {"userEnteredValue": {"stringValue": "Status"}},
            {"userEnteredValue": {"stringValue": "Progress"}},
            {"userEnteredValue": {"stringValue": "Due Date"}},
            {"userEnteredValue": {"stringValue": "Priority"}}
          ]
        }
      ],
      "columns": [
        {
          "columnId": "col_1",
          "displayName": "Task",
          "index": 0
        },
        {
          "columnId": "col_2",
          "displayName": "Status",
          "index": 1
        },
        {
          "columnId": "col_3",
          "displayName": "Progress",
          "index": 2
        },
        {
          "columnId": "col_4",
          "displayName": "Due Date",
          "index": 3
        },
        {
          "columnId": "col_5",
          "displayName": "Priority",
          "index": 4
        }
      ]
    }
  }
}
```

### 2. Delete Table (deleteTable)

Deletes a table and its contents.

**Request Type:** DeleteTableRequest
**Request:**
```json
{
  "deleteTable": {
    "tableId": "table_project_tracker"
  }
}
```

**Response:**
```json
{
  "deleteTable": {}
}
```

### 3. Update Table (updateTable)

Updates table properties like name, range, or style.

**Request Type:** UpdateTableRequest
**Request:**
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

**Response:**
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
    }
  }
}
```

### 4. Append Cells to Table (appendCells)

Adds new rows to the end of a table.

**Request Type:** AppendCellsRequest
**Request:**
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
      },
      {
        "values": [
          {"userEnteredValue": {"stringValue": "Write Tests"}},
          {"userEnteredValue": {"stringValue": "Not Started"}},
          {"userEnteredValue": {"numberValue": 0.0}},
          {"userEnteredValue": {"numberValue": 44565}},
          {"userEnteredValue": {"stringValue": "Medium"}}
        ]
      }
    ],
    "fields": "userEnteredValue,userEnteredFormat"
  }
}
```

**Response:**
```json
{
  "appendCells": {
    "updatedRange": "Sheet1!A6:B7",
    "updatedRows": 2,
    "updatedColumns": 5,
    "updatedCells": 10,
    "tableRange": "Sheet1!A1:E10"
  }
}
```

**Note:** The `tableRange` property in the response indicates the range (in A1 notation) of the table that values were appended to.

## 📝 Column Types

Tables support various column types with different behaviors:

### Text Column
```json
{
  "columnIndex": 0,
  "columnName": "Name",
  "columnType": "TEXT"
}
```

### Number Column
```json
{
  "columnIndex": 1,
  "columnName": "Age",
  "columnType": "DOUBLE"
}
```

### Date Column
```json
{
  "columnIndex": 2,
  "columnName": "Birth Date",
  "columnType": "DATE"
}
```

### Percent Column
```json
{
  "columnIndex": 3,
  "columnName": "Completion",
  "columnType": "PERCENT"
}
```

### Dropdown Column
```json
{
  "columnIndex": 4,
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

### Checkbox Column
```json
{
  "columnIndex": 5,
  "columnName": "Done",
  "columnType": "CHECKBOX"
}
```

### Smart Chip Column
```json
{
  "columnIndex": 6,
  "columnName": "Assignee",
  "columnType": "SMART_CHIP"
}
```

## 🔄 Table Operations with Other Features

### Tables with Filters
Tables can be used with filters to provide advanced data filtering:

```json
{
  "addFilterView": {
    "filter": {
      "title": "Project Filter",
      "range": {
        "sheetId": 0,
        "startRowIndex": 0,
        "endRowIndex": 10,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      },
      "sortSpecs": [
        {
          "dimensionIndex": 1,
          "sortOrder": "ASCENDING"
        }
      ],
      "filterSpecs": [
        {
          "columnIndex": 1,
          "filterCriteria": {
            "condition": {
              "type": "TEXT_EQ",
              "values": [
                {"userEnteredValue": "In Progress"}
              ]
            }
          }
        }
      ]
    }
  }
}
```

### Tables with Protected Ranges
Tables can be protected to prevent unauthorized modifications:

```json
{
  "addProtectedRange": {
    "protectedRange": {
      "range": {
        "sheetId": 0,
        "startRowIndex": 0,
        "endRowIndex": 10,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      },
      "description": "Protected table data",
      "warningOnly": false,
      "requestingUserCanEdit": true
    }
  }
}
```

## 📊 Complete Table Example

Here's a complete example of creating and managing a project tracking table:

### 1. Create the Table
```json
{
  "requests": [
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
            "endRowIndex": 1
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
            },
            {
              "columnIndex": 2,
              "columnName": "Progress",
              "columnType": "PERCENT"
            },
            {
              "columnIndex": 3,
              "columnName": "Due Date",
              "columnType": "DATE"
            },
            {
              "columnIndex": 4,
              "columnName": "Priority",
              "columnType": "DROPDOWN",
              "dataValidationRule": {
                "condition": {
                  "type": "ONE_OF_LIST",
                  "values": [
                    {"userEnteredValue": "Low"},
                    {"userEnteredValue": "Medium"},
                    {"userEnteredValue": "High"}
                  ]
                }
              }
            }
          ]
        }
      }
    }
  ]
}
```

### 2. Add Data to the Table
```json
{
  "requests": [
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
          },
          {
            "values": [
              {"userEnteredValue": {"stringValue": "Write Tests"}},
              {"userEnteredValue": {"stringValue": "Not Started"}},
              {"userEnteredValue": {"numberValue": 0.0}},
              {"userEnteredValue": {"numberValue": 44565}},
              {"userEnteredValue": {"stringValue": "Medium"}}
            ]
          }
        ],
        "fields": "userEnteredValue,userEnteredFormat"
      }
    }
  ]
}
```

### 3. Update Table Range (Add More Rows)
```json
{
  "requests": [
    {
      "updateTable": {
        "table": {
          "tableId": "table_project_tracker",
          "range": {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 10,
            "startColumnIndex": 0,
            "endColumnIndex": 5
          }
        },
        "fields": "range"
      }
    }
  ]
}
```

### 4. Sort the Table
```json
{
  "requests": [
    {
      "sortRange": {
        "range": {
          "sheetId": 0,
          "startRowIndex": 1,
          "endRowIndex": 10,
          "startColumnIndex": 0,
          "endColumnIndex": 5
        },
        "sortSpecs": [
          {
            "dimensionIndex": 1,
            "sortOrder": "ASCENDING"
          },
          {
            "dimensionIndex": 4,
            "sortOrder": "DESCENDING"
          }
        ]
      }
    }
  ]
}
```

## 📈 Pivot Tables (Related Feature)

While not the same as regular tables, pivot tables are a related feature that can be created from table data:

### Pivot Value Functions
- `PIVOT_STANDARD_VALUE_FUNCTION_UNSPECIFIED`: Default value
- `SUM`: Sum
- `COUNTA`: Count all
- `COUNT`: Count
- `COUNTUNIQUE`: Count unique
- `AVERAGE`: Average
- `MAX`: Maximum
- `MIN`: Minimum
- `MEDIAN`: Median
- `PRODUCT`: Product
- `STDEV`: Standard deviation
- `STDEVP`: Standard deviation population
- `VAR`: Variance
- `VARP`: Variance population
- `CUSTOM`: Custom

### Pivot Value Display Types
- `PIVOT_VALUE_CALCULATED_DISPLAY_TYPE_UNSPECIFIED`: Default value
- `PERCENT_OF_GRAND_TOTAL`: Percent of grand total
- `PERCENT_OF_COLUMN_TOTAL`: Percent of column total
- `PERCENT_OF_ROW_TOTAL`: Percent of row total
- `PERCENT_OF_TOTAL`: Percent of total
- `PERCENT_OF_PARENT_COLUMN_TOTAL`: Percent of parent column total
- `PERCENT_OF_PARENT_ROW_TOTAL`: Percent of parent row total
- `PERCENT_OF_PARENT_TOTAL`: Percent of parent total
- `RANK`: Rank
- `PERCENTILE`: Percentile
- `INDEX`: Index

## ⚠️ Important Notes

### 1. Table ID Requirements
- Table IDs must be unique within a spreadsheet
- Use descriptive IDs like `table_project_tracker`
- Avoid special characters in table IDs

### 2. Column Type Considerations
- **DROPDOWN columns** require `dataValidationRule` with `ONE_OF_LIST` condition
- **PERCENT columns** automatically format values as percentages
- **DATE columns** require proper date values (serial numbers)
- **CHECKBOX columns** use boolean values (true/false)

### 3. Range Management
- Tables automatically expand when using `appendCells`
- Use `updateTable` to manually adjust table ranges
- Always include header row in table range

### 4. Data Validation
- Dropdown validation is applied to entire columns
- Validation rules are enforced when data is entered
- Invalid data will be rejected by the API

### 5. Performance Considerations
- Use batch operations for multiple table operations
- Limit table size for better performance
- Consider using filters for large datasets

### 6. Data Validation Rule Properties
- `condition` (BooleanCondition): The condition that data must match
- `inputMessage` (string): Message shown when adding data to cell
- `strict` (boolean): True if invalid data should be rejected
- `showCustomUi` (boolean): True if custom help text should be shown

## 🔗 Related Documentation

- [Google Sheets API Overview](01_API_Overview.md)
- [Batch Operations](04_Batch_Operations.md)
- [Request Examples](13_Request_Examples.md)
- [Error Handling](10_Error_Handling.md)
- [Rate Limits](11_Rate_Limits.md)

## 📚 Additional Resources

- [Google Sheets API Tables Guide](https://developers.google.com/workspace/sheets/api/guides/tables)
- [Google Sheets API Reference](https://developers.google.com/sheets/api/reference/rest)
- [Google Sheets API Samples](https://github.com/googleapis/google-api-python-client-samples)

---

*This documentation is based on Google Sheets API v4 and covers all table-related operations and features.* 