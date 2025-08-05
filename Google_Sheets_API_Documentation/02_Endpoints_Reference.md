# Google Sheets API v4 - Endpoints Reference

## 📋 Overview

This document covers all 13 endpoints of the Google Sheets API v4, organized by resource type.

## 🏗️ API Resources

### 1. Spreadsheets Resource

#### 1.1 Get Spreadsheet
```
GET /v4/spreadsheets/{spreadsheetId}
```

**Description:** Returns the spreadsheet at the given ID.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve
- `ranges` (query, optional): The ranges to retrieve from the spreadsheet
- `includeGridData` (query, optional): True if grid data should be returned
- `fields` (query, optional): The fields to include in the response

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
```

#### 1.2 Batch Update
```
POST /v4/spreadsheets/{spreadsheetId}:batchUpdate
```

**Description:** Applies one or more updates to the spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchUpdateSpreadsheetRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "updateCells": {
          "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 2},
          "rows": [{"values": [{"userEnteredValue": {"stringValue": "Hello"}}, {"userEnteredValue": {"stringValue": "World"}}]}],
          "fields": "userEnteredValue"
        }
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID:batchUpdate"
```

### 2. Values Resource

#### 2.1 Get Values
```
GET /v4/spreadsheets/{spreadsheetId}/values/{range}
```

**Description:** Returns a range of values from a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve data from
- `range` (path, required): The A1 notation or R1C1 notation of the values to retrieve
- `majorDimension` (query, optional): The major dimension that results should use
- `valueRenderOption` (query, optional): How values should be rendered in the output
- `dateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:B10"
```

#### 2.2 Update Values
```
PUT /v4/spreadsheets/{spreadsheetId}/values/{range}
```

**Description:** Sets values in a range of a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update
- `range` (path, required): The A1 notation of the values to update
- `valueInputOption` (query, optional): How the input data should be interpreted
- `includeValuesInResponse` (query, optional): Whether to include updated values in response
- `responseValueRenderOption` (query, optional): How values should be rendered in response
- `responseDateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Request Body:** ValueRange

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "range": "Sheet1!A1:B2",
    "majorDimension": "ROWS",
    "values": [["Hello", "World"], ["Data", "Row 2"]]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:B2?valueInputOption=USER_ENTERED"
```

#### 2.3 Append Values
```
POST /v4/spreadsheets/{spreadsheetId}/values/{range}:append
```

**Description:** Appends values to a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update
- `range` (path, required): The A1 notation of a range to search for a logical table of data
- `valueInputOption` (query, optional): How the input data should be interpreted
- `insertDataOption` (query, optional): How the input data should be inserted
- `includeValuesInResponse` (query, optional): Whether to include updated values in response
- `responseValueRenderOption` (query, optional): How values should be rendered in response
- `responseDateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Request Body:** ValueRange

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "range": "Sheet1!A:B",
    "majorDimension": "ROWS",
    "values": [["New", "Data"], ["Row", "3"]]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A:B:append?valueInputOption=USER_ENTERED"
```

#### 2.4 Clear Values
```
POST /v4/spreadsheets/{spreadsheetId}/values/{range}:clear
```

**Description:** Clears values from a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update
- `range` (path, required): The A1 notation of the values to clear

**Request Body:** ClearValuesRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:B10:clear"
```

#### 2.5 Batch Get Values
```
GET /v4/spreadsheets/{spreadsheetId}/values:batchGet
```

**Description:** Returns one or more ranges of values from a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve data from
- `ranges` (query, required): The A1 notation or R1C1 notation of the values to retrieve
- `majorDimension` (query, optional): The major dimension that results should use
- `valueRenderOption` (query, optional): How values should be rendered in the output
- `dateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values:batchGet?ranges=Sheet1!A1:B10&ranges=Sheet1!D1:E10"
```

#### 2.6 Batch Update Values
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchUpdate
```

**Description:** Sets values in one or more ranges of a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchUpdateValuesRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "valueInputOption": "USER_ENTERED",
    "data": [
      {
        "range": "Sheet1!A1:B2",
        "majorDimension": "ROWS",
        "values": [["Hello", "World"], ["Data", "Row 2"]]
      },
      {
        "range": "Sheet1!D1:E2",
        "majorDimension": "ROWS",
        "values": [["More", "Data"], ["Row", "3"]]
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values:batchUpdate"
```

#### 2.7 Batch Clear Values
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchClear
```

**Description:** Clears one or more ranges of values from a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchClearValuesRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ranges": ["Sheet1!A1:B10", "Sheet1!D1:E10"]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values:batchClear"
```

#### 2.8 Batch Get Values By Data Filter
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchGetByDataFilter
```

**Description:** Returns one or more ranges of values that match the specified data filters.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve data from

**Request Body:** BatchGetValuesByDataFilterRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataFilters": [
      {
        "a1Range": "Sheet1!A1:B10"
      }
    ],
    "majorDimension": "ROWS"
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values:batchGetByDataFilter"
```

#### 2.9 Batch Update Values By Data Filter
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchUpdateByDataFilter
```

**Description:** Sets values in one or more ranges of a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchUpdateValuesByDataFilterRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "valueInputOption": "USER_ENTERED",
    "data": [
      {
        "dataFilter": {
          "a1Range": "Sheet1!A1:B10"
        },
        "majorDimension": "ROWS",
        "valueRange": {
          "range": "Sheet1!A1:B10",
          "majorDimension": "ROWS",
          "values": [["Hello", "World"], ["Data", "Row 2"]]
        }
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values:batchUpdateByDataFilter"
```

#### 2.10 Batch Clear Values By Data Filter
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchClearByDataFilter
```

**Description:** Clears one or more ranges of values from a spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchClearValuesByDataFilterRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataFilters": [
      {
        "a1Range": "Sheet1!A1:B10"
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values:batchClearByDataFilter"
```

### 3. Developer Metadata Resource

#### 3.1 Get Developer Metadata
```
GET /v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}
```

**Description:** Returns the developer metadata with the specified ID.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve metadata from
- `metadataId` (path, required): The ID of the developer metadata to retrieve

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/developerMetadata/METADATA_ID"
```

#### 3.2 Search Developer Metadata
```
POST /v4/spreadsheets/{spreadsheetId}/developerMetadata:search
```

**Description:** Returns all developer metadata matching the specified data filters.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve metadata from

**Request Body:** SearchDeveloperMetadataRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataFilters": [
      {
        "developerMetadataLookup": {
          "metadataKey": "my-key"
        }
      }
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/developerMetadata:search"
```

### 4. Sheets Resource

#### 4.1 Copy Sheet
```
POST /v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo
```

**Description:** Copies a single sheet from a spreadsheet to another spreadsheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet containing the sheet to copy
- `sheetId` (path, required): The ID of the sheet to copy

**Request Body:** CopySheetToAnotherSpreadsheetRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destinationSpreadsheetId": "DESTINATION_SPREADSHEET_ID"
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/SOURCE_SPREADSHEET_ID/sheets/SHEET_ID:copyTo"
```

## 🔗 Related Documentation

- **[API Overview](01_API_Overview.md)** - Basic API information and setup
- **[Schemas Reference](03_Schemas_Reference.md)** - Complete schema definitions
- **[Batch Operations](04_Batch_Operations.md)** - Batch update request types
- **[Error Handling](10_Error_Handling.md)** - Error codes and troubleshooting
- **[Request Examples](13_Request_Examples.md)** - Common request patterns 