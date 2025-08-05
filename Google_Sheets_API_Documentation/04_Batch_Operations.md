# Google Sheets API v4 - Batch Operations

## 📋 Overview

Batch operations allow you to perform multiple updates to a spreadsheet in a single API call, improving efficiency and reducing the number of requests needed.

## 🔄 Batch Update Endpoint

```
POST /v4/spreadsheets/{spreadsheetId}:batchUpdate
```

**Description:** Applies one or more updates to the spreadsheet.

**Request Body:** BatchUpdateSpreadsheetRequest

## 📝 Request Types

### 1. Update Cells
Updates all cells in a range with new data.

```json
{
  "updateCells": {
    "range": {
      "sheetId": 0,
      "startRowIndex": 0,
      "endRowIndex": 2,
      "startColumnIndex": 0,
      "endColumnIndex": 2
    },
    "rows": [
      {
        "values": [
          {"userEnteredValue": {"stringValue": "Hello"}},
          {"userEnteredValue": {"stringValue": "World"}}
        ]
      }
    ],
    "fields": "userEnteredValue,userEnteredFormat"
  }
}
```

### 2. Insert Dimension
Inserts rows or columns in a sheet.

```json
{
  "insertDimension": {
    "range": {
      "sheetId": 0,
      "dimension": "ROWS",
      "startIndex": 5,
      "endIndex": 7
    },
    "inheritFromBefore": true
  }
}
```

### 3. Delete Dimension
Deletes rows or columns in a sheet.

```json
{
  "deleteDimension": {
    "range": {
      "sheetId": 0,
      "dimension": "COLUMNS",
      "startIndex": 2,
      "endIndex": 4
    }
  }
}
```

### 4. Update Sheet Properties
Updates the properties of a sheet.

```json
{
  "updateSheetProperties": {
    "properties": {
      "sheetId": 0,
      "title": "Updated Sheet Name",
      "hidden": false
    },
    "fields": "title,hidden"
  }
}
```

### 5. Add Sheet
Adds a new sheet.

```json
{
  "addSheet": {
    "properties": {
      "title": "New Sheet",
      "gridProperties": {
        "rowCount": 1000,
        "columnCount": 26
      }
    }
  }
}
```

### 6. Delete Sheet
Deletes a sheet.

```json
{
  "deleteSheet": {
    "sheetId": 1
  }
}
```

### 7. Duplicate Sheet
Duplicates a sheet.

```json
{
  "duplicateSheet": {
    "sourceSheetId": 0,
    "insertSheetIndex": 1,
    "newSheetName": "Copy of Sheet1"
  }
}
```

### 8. Update Borders
Updates the borders of a range of cells.

```json
{
  "updateBorders": {
    "range": {
      "sheetId": 0,
      "startRowIndex": 0,
      "endRowIndex": 5,
      "startColumnIndex": 0,
      "endColumnIndex": 5
    },
    "top": {
      "style": "SOLID",
      "color": {"red": 0, "green": 0, "blue": 0}
    },
    "bottom": {
      "style": "SOLID",
      "color": {"red": 0, "green": 0, "blue": 0}
    },
    "left": {
      "style": "SOLID",
      "color": {"red": 0, "green": 0, "blue": 0}
    },
    "right": {
      "style": "SOLID",
      "color": {"red": 0, "green": 0, "blue": 0}
    }
  }
}
```

### 9. Update Conditional Format Rule
Updates a conditional format rule at the given index.

```json
{
  "updateConditionalFormatRule": {
    "sheetId": 0,
    "index": 0,
    "rule": {
      "ranges": [
        {
          "sheetId": 0,
          "startRowIndex": 0,
          "endRowIndex": 10,
          "startColumnIndex": 0,
          "endColumnIndex": 5
        }
      ],
      "booleanRule": {
        "condition": {
          "type": "NUMBER_GREATER",
          "values": [{"userEnteredValue": "0"}]
        },
        "format": {
          "backgroundColor": {"red": 1, "green": 0, "blue": 0}
        }
      }
    }
  }
}
```

### 10. Add Conditional Format Rule
Adds a new conditional format rule.

```json
{
  "addConditionalFormatRule": {
    "rule": {
      "ranges": [
        {
          "sheetId": 0,
          "startRowIndex": 0,
          "endRowIndex": 10,
          "startColumnIndex": 0,
          "endColumnIndex": 5
        }
      ],
      "gradientRule": {
        "minpoint": {
          "color": {"red": 1, "green": 0, "blue": 0},
          "type": "MIN"
        },
        "maxpoint": {
          "color": {"red": 0, "green": 1, "blue": 0},
          "type": "MAX"
        }
      }
    }
  }
}
```

### 11. Delete Conditional Format Rule
Deletes a conditional format rule at the given index.

```json
{
  "deleteConditionalFormatRule": {
    "sheetId": 0,
    "index": 0
  }
}
```

### 12. Update Chart Spec
Updates a chart's specifications.

```json
{
  "updateChartSpec": {
    "chartId": 123,
    "spec": {
      "title": "Updated Chart Title",
      "basicChart": {
        "chartType": "COLUMN",
        "legendPosition": "BOTTOM_LEGEND",
        "axis": [
          {
            "position": "BOTTOM_AXIS",
            "title": "X Axis"
          }
        ],
        "domains": [
          {
            "domain": {
              "sourceRange": {
                "sources": [
                  {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5
                  }
                ]
              }
            }
          }
        ]
      }
    }
  }
}
```

### 13. Add Chart
Adds a chart to the sheet.

```json
{
  "addChart": {
    "chart": {
      "spec": {
        "title": "New Chart",
        "basicChart": {
          "chartType": "LINE",
          "legendPosition": "RIGHT_LEGEND"
        }
      },
      "position": {
        "overlayPosition": {
          "anchorCell": {
            "sheetId": 0,
            "rowIndex": 0,
            "columnIndex": 0
          },
          "offsetXPixels": 0,
          "offsetYPixels": 0,
          "widthPixels": 400,
          "heightPixels": 300
        }
      }
    }
  }
}
```

### 14. Update Named Range
Updates a named range.

```json
{
  "updateNamedRange": {
    "namedRangeId": "range1",
    "namedRange": {
      "name": "Updated Range",
      "range": {
        "sheetId": 0,
        "startRowIndex": 0,
        "endRowIndex": 10,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      }
    },
    "fields": "name,range"
  }
}
```

### 15. Add Named Range
Adds a named range.

```json
{
  "addNamedRange": {
    "namedRange": {
      "name": "My Range",
      "range": {
        "sheetId": 0,
        "startRowIndex": 0,
        "endRowIndex": 10,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      }
    }
  }
}
```

### 16. Delete Named Range
Removes a named range.

```json
{
  "deleteNamedRange": {
    "namedRangeId": "range1"
  }
}
```

### 17. Update Developer Metadata
Updates developer metadata.

```json
{
  "updateDeveloperMetadata": {
    "dataFilters": [
      {
        "developerMetadataLookup": {
          "metadataKey": "my-key"
        }
      }
    ],
    "developerMetadata": {
      "metadataKey": "updated-key",
      "metadataValue": "updated-value"
    },
    "fields": "metadataKey,metadataValue"
  }
}
```

### 18. Delete Developer Metadata
Removes developer metadata.

```json
{
  "deleteDeveloperMetadata": {
    "dataFilters": [
      {
        "developerMetadataLookup": {
          "metadataKey": "my-key"
        }
      }
    ]
  }
}
```

### 19. Auto Resize Dimensions
Automatically resizes one or more dimensions based on the contents of the cells.

```json
{
  "autoResizeDimensions": {
    "dimensions": {
      "sheetId": 0,
      "dimension": "COLUMNS",
      "startIndex": 0,
      "endIndex": 5
    }
  }
}
```

### 20. Move Dimension
Moves one or more rows or columns.

```json
{
  "moveDimension": {
    "source": {
      "sheetId": 0,
      "dimension": "ROWS",
      "startIndex": 5,
      "endIndex": 7
    },
    "destinationIndex": 10
  }
}
```

### 21. Update Dimension Properties
Updates the properties of dimensions within the specified range.

```json
{
  "updateDimensionProperties": {
    "range": {
      "sheetId": 0,
      "dimension": "COLUMNS",
      "startIndex": 0,
      "endIndex": 5
    },
    "properties": {
      "hiddenByUser": false,
      "pixelSize": 100
    },
    "fields": "hiddenByUser,pixelSize"
  }
}
```

### 22. Update Sheet Properties
Updates the properties of a sheet.

```json
{
  "updateSheetProperties": {
    "properties": {
      "sheetId": 0,
      "title": "Updated Sheet",
      "hidden": false,
      "tabColor": {
        "red": 1,
        "green": 0,
        "blue": 0
      }
    },
    "fields": "title,hidden,tabColor"
  }
}
```

### 23. Update Spreadsheet Properties
Updates the properties of a spreadsheet.

```json
{
  "updateSpreadsheetProperties": {
    "properties": {
      "title": "Updated Spreadsheet",
      "locale": "en_US",
      "timeZone": "America/New_York"
    },
    "fields": "title,locale,timeZone"
  }
}
```

### 24. Update Table
Updates a table.

```json
{
  "updateTable": {
    "table": {
      "tableId": 1,
      "displayName": "Updated Table",
      "range": {
        "sheetId": 0,
        "startRowIndex": 0,
        "endRowIndex": 10,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      }
    },
    "fields": "displayName,range"
  }
}
```

### 25. Refresh Data Source
Refreshes one or more data source objects.

```json
{
  "refreshDataSource": {
    "dataSourceId": "ds_123",
    "force": true
  }
}
```

## 🔄 Complete Batch Update Example

```json
{
  "requests": [
    {
      "updateCells": {
        "range": {
          "sheetId": 0,
          "startRowIndex": 0,
          "endRowIndex": 2,
          "startColumnIndex": 0,
          "endColumnIndex": 2
        },
        "rows": [
          {
            "values": [
              {"userEnteredValue": {"stringValue": "Hello"}},
              {"userEnteredValue": {"stringValue": "World"}}
            ]
          }
        ],
        "fields": "userEnteredValue"
      }
    },
    {
      "insertDimension": {
        "range": {
          "sheetId": 0,
          "dimension": "ROWS",
          "startIndex": 5,
          "endIndex": 7
        },
        "inheritFromBefore": true
      }
    },
    {
      "updateSheetProperties": {
        "properties": {
          "sheetId": 0,
          "title": "Updated Sheet"
        },
        "fields": "title"
      }
    }
  ],
  "includeSpreadsheetInResponse": true,
  "responseRanges": ["Sheet1!A1:B2"],
  "responseIncludeGridData": true
}
```

## 📊 Response Format

```json
{
  "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "replies": [
    {
      "updateCells": {
        "updatedRange": "Sheet1!A1:B2",
        "updatedRows": 2,
        "updatedColumns": 2,
        "updatedCells": 4
      }
    },
    {
      "insertDimension": {}
    },
    {
      "updateSheetProperties": {}
    }
  ],
  "updatedSpreadsheet": {
    "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "properties": {
      "title": "My Spreadsheet"
    },
    "sheets": [...]
  }
}
```

## 💡 Best Practices

1. **Group Related Operations**: Combine related updates in a single batch request
2. **Use Fields Parameter**: Only update the fields you need to change
3. **Handle Errors**: Check the response for any failed operations
4. **Limit Batch Size**: Keep batch requests reasonable in size
5. **Use Response Data**: Include response data when you need the updated state

## 🔗 Related Documentation

- **[API Overview](01_API_Overview.md)** - Basic API information
- **[Endpoints Reference](02_Endpoints_Reference.md)** - All API endpoints
- **[Schemas Reference](03_Schemas_Reference.md)** - Complete schema definitions
- **[Error Handling](10_Error_Handling.md)** - Error codes and troubleshooting 