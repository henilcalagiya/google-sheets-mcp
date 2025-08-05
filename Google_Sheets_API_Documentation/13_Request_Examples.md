# Google Sheets API v4 - Request Examples

## 📋 Overview

This document provides practical examples of common Google Sheets API v4 requests, organized by use case and complexity.

## 🔧 Basic Operations

### 1. Read Values from a Range

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Initialize the service
service = build('sheets', 'v4', credentials=credentials)

# Read a single range
result = service.spreadsheets().values().get(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    range='Sheet1!A1:B10'
).execute()

print('Values:', result.get('values', []))
```

### 2. Write Values to a Range

```python
# Write data to a range
body = {
    'values': [
        ['Name', 'Age', 'City'],
        ['John', 25, 'New York'],
        ['Jane', 30, 'Los Angeles'],
        ['Bob', 35, 'Chicago']
    ]
}

result = service.spreadsheets().values().update(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    range='Sheet1!A1:C4',
    valueInputOption='USER_ENTERED',
    body=body
).execute()

print('Updated cells:', result.get('updatedCells'))
```

### 3. Append Values to a Range

```python
# Append data to the end of existing data
body = {
    'values': [
        ['Alice', 28, 'Boston'],
        ['Charlie', 32, 'Seattle']
    ]
}

result = service.spreadsheets().values().append(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    range='Sheet1!A:C',
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body=body
).execute()

print('Appended range:', result.get('updates').get('updatedRange'))
```

## 📊 Batch Operations

### 4. Batch Read Multiple Ranges

```python
# Read multiple ranges in a single request
result = service.spreadsheets().values().batchGet(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    ranges=['Sheet1!A1:B10', 'Sheet1!D1:E10', 'Sheet2!A1:A5']
).execute()

valueRanges = result.get('valueRanges', [])
for valueRange in valueRanges:
    print('Range:', valueRange.get('range'))
    print('Values:', valueRange.get('values', []))
```

### 5. Batch Update Multiple Ranges

```python
# Update multiple ranges in a single request
body = {
    'valueInputOption': 'USER_ENTERED',
    'data': [
        {
            'range': 'Sheet1!A1:B3',
            'values': [['Header1', 'Header2'], ['Data1', 'Data2'], ['Data3', 'Data4']]
        },
        {
            'range': 'Sheet1!D1:E3',
            'values': [['Header3', 'Header4'], ['Data5', 'Data6'], ['Data7', 'Data8']]
        }
    ]
}

result = service.spreadsheets().values().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()

print('Total updated cells:', result.get('totalUpdatedCells'))
```

### 6. Clear Multiple Ranges

```python
# Clear multiple ranges
body = {
    'ranges': ['Sheet1!A1:B10', 'Sheet1!D1:E10']
}

result = service.spreadsheets().values().batchClear(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()

print('Cleared ranges:', result.get('clearedRanges'))
```

## 🎨 Formatting Operations

### 7. Update Cell Formatting

```python
# Update cell formatting using batchUpdate
body = {
    'requests': [
        {
            'updateCells': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 3
                },
                'rows': [
                    {
                        'values': [
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 1, 'green': 0, 'blue': 0},
                                    'textFormat': {
                                        'bold': True,
                                        'fontSize': 12,
                                        'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                                    }
                                }
                            },
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0, 'green': 1, 'blue': 0},
                                    'textFormat': {
                                        'bold': True,
                                        'fontSize': 12,
                                        'foregroundColor': {'red': 0, 'green': 0, 'blue': 0}
                                    }
                                }
                            },
                            {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0, 'green': 0, 'blue': 1},
                                    'textFormat': {
                                        'bold': True,
                                        'fontSize': 12,
                                        'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                                    }
                                }
                            }
                        ]
                    }
                ],
                'fields': 'userEnteredFormat'
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

### 8. Add Borders

```python
# Add borders to a range
body = {
    'requests': [
        {
            'updateBorders': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 5,
                    'startColumnIndex': 0,
                    'endColumnIndex': 3
                },
                'top': {
                    'style': 'SOLID',
                    'color': {'red': 0, 'green': 0, 'blue': 0}
                },
                'bottom': {
                    'style': 'SOLID',
                    'color': {'red': 0, 'green': 0, 'blue': 0}
                },
                'left': {
                    'style': 'SOLID',
                    'color': {'red': 0, 'green': 0, 'blue': 0}
                },
                'right': {
                    'style': 'SOLID',
                    'color': {'red': 0, 'green': 0, 'blue': 0}
                },
                'innerHorizontal': {
                    'style': 'DASHED',
                    'color': {'red': 0.5, 'green': 0.5, 'blue': 0.5}
                },
                'innerVertical': {
                    'style': 'DASHED',
                    'color': {'red': 0.5, 'green': 0.5, 'blue': 0.5}
                }
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

## 📋 Conditional Formatting

### 9. Add Conditional Formatting Rule

```python
# Add a conditional formatting rule
body = {
    'requests': [
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [
                        {
                            'sheetId': 0,
                            'startRowIndex': 1,
                            'endRowIndex': 10,
                            'startColumnIndex': 1,
                            'endColumnIndex': 2
                        }
                    ],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_GREATER',
                            'values': [{'userEnteredValue': '50'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 1, 'green': 0, 'blue': 0}
                        }
                    }
                }
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

### 10. Add Gradient Conditional Formatting

```python
# Add gradient conditional formatting
body = {
    'requests': [
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [
                        {
                            'sheetId': 0,
                            'startRowIndex': 1,
                            'endRowIndex': 10,
                            'startColumnIndex': 1,
                            'endColumnIndex': 2
                        }
                    ],
                    'gradientRule': {
                        'minpoint': {
                            'color': {'red': 1, 'green': 0, 'blue': 0},
                            'type': 'MIN'
                        },
                        'maxpoint': {
                            'color': {'red': 0, 'green': 1, 'blue': 0},
                            'type': 'MAX'
                        }
                    }
                }
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

## 📈 Chart Operations

### 11. Add a Basic Chart

```python
# Add a basic column chart
body = {
    'requests': [
        {
            'addChart': {
                'chart': {
                    'spec': {
                        'title': 'Sales Data',
                        'basicChart': {
                            'chartType': 'COLUMN',
                            'legendPosition': 'BOTTOM_LEGEND',
                            'axis': [
                                {
                                    'position': 'BOTTOM_AXIS',
                                    'title': 'Month'
                                },
                                {
                                    'position': 'LEFT_AXIS',
                                    'title': 'Sales'
                                }
                            ],
                            'domains': [
                                {
                                    'domain': {
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': 0,
                                                    'startRowIndex': 0,
                                                    'endRowIndex': 1,
                                                    'startColumnIndex': 0,
                                                    'endColumnIndex': 4
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            'series': [
                                {
                                    'series': {
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': 0,
                                                    'startRowIndex': 1,
                                                    'endRowIndex': 4,
                                                    'startColumnIndex': 1,
                                                    'endColumnIndex': 2
                                                }
                                            ]
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS'
                                }
                            ]
                        }
                    },
                    'position': {
                        'overlayPosition': {
                            'anchorCell': {
                                'sheetId': 0,
                                'rowIndex': 0,
                                'columnIndex': 5
                            },
                            'offsetXPixels': 0,
                            'offsetYPixels': 0,
                            'widthPixels': 400,
                            'heightPixels': 300
                        }
                    }
                }
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

## 🔧 Sheet Operations

### 12. Add a New Sheet

```python
# Add a new sheet
body = {
    'requests': [
        {
            'addSheet': {
                'properties': {
                    'title': 'New Sheet',
                    'gridProperties': {
                        'rowCount': 1000,
                        'columnCount': 26
                    },
                    'tabColor': {
                        'red': 1,
                        'green': 0,
                        'blue': 0
                    }
                }
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

### 13. Duplicate a Sheet

```python
# Duplicate an existing sheet
body = {
    'requests': [
        {
            'duplicateSheet': {
                'sourceSheetId': 0,
                'insertSheetIndex': 1,
                'newSheetName': 'Copy of Sheet1'
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

### 14. Delete a Sheet

```python
# Delete a sheet
body = {
    'requests': [
        {
            'deleteSheet': {
                'sheetId': 1
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

## 📊 Data Validation

### 15. Add Data Validation

```python
# Add data validation to a range
body = {
    'requests': [
        {
            'updateCells': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 1,
                    'endRowIndex': 10,
                    'startColumnIndex': 0,
                    'endColumnIndex': 1
                },
                'rows': [
                    {
                        'values': [
                            {
                                'dataValidation': {
                                    'condition': {
                                        'type': 'ONE_OF_LIST',
                                        'values': [
                                            {'userEnteredValue': 'Option 1'},
                                            {'userEnteredValue': 'Option 2'},
                                            {'userEnteredValue': 'Option 3'}
                                        ]
                                    },
                                    'showCustomUi': True,
                                    'strict': True
                                }
                            }
                        ]
                    }
                ],
                'fields': 'dataValidation'
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

## 🔧 Developer Metadata

### 16. Add Developer Metadata

```python
# Add developer metadata to a range
body = {
    'requests': [
        {
            'updateDeveloperMetadata': {
                'dataFilters': [
                    {
                        'developerMetadataLookup': {
                            'metadataKey': 'status'
                        }
                    }
                ],
                'developerMetadata': {
                    'metadataKey': 'status',
                    'metadataValue': 'active',
                    'location': {
                        'locationType': 'ROW',
                        'dimensionRange': {
                            'sheetId': 0,
                            'dimension': 'ROWS',
                            'startIndex': 0,
                            'endIndex': 1
                        }
                    },
                    'visibility': 'DOCUMENT'
                },
                'fields': 'metadataKey,metadataValue,location,visibility'
            }
        }
    ]
}

result = service.spreadsheets().batchUpdate(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    body=body
).execute()
```

## 🔄 Error Handling Examples

### 17. Handle API Errors

```python
from googleapiclient.errors import HttpError

def safe_api_call(service, request_func):
    try:
        return request_func()
    except HttpError as error:
        if error.resp.status == 404:
            print("Spreadsheet not found")
        elif error.resp.status == 403:
            print("Permission denied")
        elif error.resp.status == 429:
            print("Rate limit exceeded")
        else:
            print(f"API Error: {error.resp.status} - {error.content}")
        return None

# Usage
result = safe_api_call(service, lambda: service.spreadsheets().values().get(
    spreadsheetId='invalid-id',
    range='Sheet1!A1:B10'
).execute())
```

### 18. Retry with Exponential Backoff

```python
import time
import random
from googleapiclient.errors import HttpError

def retry_with_backoff(service, request_func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return request_func()
        except HttpError as error:
            if error.resp.status == 429 and attempt < max_retries - 1:
                wait_time = min(2 ** attempt + random.uniform(0, 1), 60)
                print(f"Rate limited, waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise error
    
    raise Exception("Max retries exceeded")

# Usage
result = retry_with_backoff(service, lambda: service.spreadsheets().values().get(
    spreadsheetId='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
    range='Sheet1!A1:B10'
).execute())
```

## 🔗 Related Documentation

- **[API Overview](01_API_Overview.md)** - Basic API information
- **[Endpoints Reference](02_Endpoints_Reference.md)** - All API endpoints
- **[Batch Operations](04_Batch_Operations.md)** - Batch update operations
- **[Error Handling](10_Error_Handling.md)** - Error codes and troubleshooting
- **[Rate Limits](11_Rate_Limits.md)** - Quota management

---

*These examples demonstrate common patterns for working with the Google Sheets API v4. Adapt them to your specific use cases and requirements.* 