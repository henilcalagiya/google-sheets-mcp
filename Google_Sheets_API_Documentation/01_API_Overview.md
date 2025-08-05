# Google Sheets API v4 - API Overview

## 📋 Basic Information

**API Version:** v4  
**Base URL:** `https://sheets.googleapis.com/$discovery/rest?version=v4`  
**Description:** Reads and writes Google Sheets  
**Revision:** 20250728

## 🔐 Authentication & Scopes

### Required Scopes
- `https://www.googleapis.com/auth/spreadsheets` - Full access to spreadsheets
- `https://www.googleapis.com/auth/spreadsheets.readonly` - Read-only access
- `https://www.googleapis.com/auth/drive` - Full access to Drive
- `https://www.googleapis.com/auth/drive.file` - Access to files created by the app
- `https://www.googleapis.com/auth/drive.readonly` - Read-only access to Drive

### Authentication Methods
1. **OAuth 2.0** - For user-based applications
2. **Service Account** - For server-to-server applications
3. **API Key** - For public data access (limited)

## 🏗️ API Resources

### 1. Spreadsheets Resource
- **Get Spreadsheet** - Retrieve spreadsheet data
- **Batch Update** - Apply multiple operations

### 2. Values Resource
- **Get Values** - Read cell values
- **Update Values** - Write cell values
- **Append Values** - Add data to end
- **Clear Values** - Remove cell data
- **Batch Operations** - Multiple value operations

### 3. Developer Metadata Resource
- **Get Developer Metadata** - Retrieve metadata
- **Search Developer Metadata** - Find metadata

### 4. Sheets Resource
- **Copy Sheet** - Duplicate sheets between spreadsheets

## 📊 Data Structures

### Core Concepts
- **Spreadsheet** - The main container
- **Sheet** - Individual worksheets
- **Range** - Cell ranges (A1 notation)
- **Value** - Cell data
- **Format** - Cell styling

### Key Schemas
- **ValueRange** - Data within a range
- **GridRange** - Range on a sheet
- **CellData** - Individual cell data
- **CellFormat** - Cell formatting
- **SheetProperties** - Sheet configuration

## 🔄 Common Operations

### Reading Data
```javascript
// Get a range of values
GET /v4/spreadsheets/{spreadsheetId}/values/{range}

// Get multiple ranges
GET /v4/spreadsheets/{spreadsheetId}/values:batchGet
```

### Writing Data
```javascript
// Update a range of values
PUT /v4/spreadsheets/{spreadsheetId}/values/{range}

// Append values
POST /v4/spreadsheets/{spreadsheetId}/values/{range}:append
```

### Complex Operations
```javascript
// Batch update with multiple operations
POST /v4/spreadsheets/{spreadsheetId}:batchUpdate
```

## 📈 Rate Limits

### Standard Limits
- **Read requests:** 300 requests per minute per user
- **Write requests:** 60 requests per minute per user
- **Batch requests:** Count as single request
- **Developer metadata:** 100 requests per minute per user

### Quota Management
- Monitor usage with quota headers
- Implement exponential backoff
- Use batch operations when possible

## 🛠️ Setup Guide

### 1. Enable the API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the Google Sheets API
4. Create credentials (OAuth 2.0 or Service Account)

### 2. Install Client Library
```bash
# Python
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Node.js
npm install googleapis

# Java
<dependency>
    <groupId>com.google.apis</groupId>
    <artifactId>google-api-services-sheets</artifactId>
    <version>v4-rev20220927-2.0.0</version>
</dependency>
```

### 3. Basic Usage Example
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Initialize the service
service = build('sheets', 'v4', credentials=credentials)

# Read data
result = service.spreadsheets().values().get(
    spreadsheetId='your-spreadsheet-id',
    range='A1:B10'
).execute()

# Write data
body = {
    'values': [['Hello', 'World'], ['Data', 'Row 2']]
}
result = service.spreadsheets().values().update(
    spreadsheetId='your-spreadsheet-id',
    range='A1:B2',
    valueInputOption='USER_ENTERED',
    body=body
).execute()
```

## 🔗 Related Documentation

- **[Endpoints Reference](02_Endpoints_Reference.md)** - Detailed endpoint documentation
- **[Schemas Reference](03_Schemas_Reference.md)** - Complete schema definitions
- **[Error Handling](10_Error_Handling.md)** - Error codes and troubleshooting
- **[Rate Limits](11_Rate_Limits.md)** - Detailed quota information

## 📚 External Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Sheets API Reference](https://developers.google.com/sheets/api/reference/rest)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) 