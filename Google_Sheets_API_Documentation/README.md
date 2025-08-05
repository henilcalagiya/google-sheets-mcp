# Google Sheets API v4 - Complete Documentation

This folder contains comprehensive documentation for the Google Sheets API v4, organized into separate files for better navigation and reference.

## 📚 Documentation Structure

### Complete Reference
- **[Complete Reference](00_Complete_Reference.md)** - All 130 schemas, endpoints, and complete API reference (comprehensive)

### Core Documentation
- **[API Overview](01_API_Overview.md)** - Basic API information, authentication, and setup
- **[Endpoints Reference](02_Endpoints_Reference.md)** - All 13 API endpoints with parameters and examples
- **[Schemas Reference](03_Schemas_Reference.md)** - All 130 schemas with properties and types

### Specialized Documentation
- **[Batch Operations](04_Batch_Operations.md)** - All 25 batch update request types and examples
- **[Chart Specifications](05_Chart_Specifications.md)** - All chart types and their configurations
- **[Conditional Formatting](06_Conditional_Formatting.md)** - Formatting rules and conditions
- **[Pivot Tables](07_Pivot_Tables.md)** - Pivot table operations and structures
- **[Data Sources](08_Data_Sources.md)** - BigQuery integration and data source operations
- **[Developer Metadata](09_Developer_Metadata.md)** - Metadata operations and structures

### Reference Documentation
- **[Error Handling](10_Error_Handling.md)** - All error codes, responses, and troubleshooting
- **[Rate Limits](11_Rate_Limits.md)** - API quotas and rate limiting information
- **[Enum Values](12_Enum_Values.md)** - All enum values and their meanings
- **[Request Examples](13_Request_Examples.md)** - Common request patterns and examples

## 🚀 Quick Start

1. **Start with** [API Overview](01_API_Overview.md) for basic setup
2. **Check** [Endpoints Reference](02_Endpoints_Reference.md) for available operations
3. **Reference** [Schemas Reference](03_Schemas_Reference.md) for data structures
4. **Use** [Batch Operations](04_Batch_Operations.md) for complex operations
5. **Consult** [Error Handling](10_Error_Handling.md) for troubleshooting

## 📋 API Summary

- **API Version:** v4
- **Base URL:** `https://sheets.googleapis.com/$discovery/rest?version=v4`
- **Total Endpoints:** 13
- **Total Schemas:** 130
- **Batch Operations:** 25
- **Chart Types:** 9
- **Condition Types:** 40+

## 🔍 Documentation Features

### ✅ Complete Coverage
- **All 130 schemas** with properties and types
- **All 13 endpoints** with parameters and examples
- **All 25 batch operations** with JSON examples
- **All error codes** and troubleshooting guides
- **All rate limits** and quota management
- **All enum values** and their meanings

### 📖 Easy Navigation
- **Modular structure** - Find exactly what you need
- **Cross-references** - Links between related topics
- **Code examples** - Ready-to-use code snippets
- **Best practices** - Implementation guidelines

### 🛠️ Practical Focus
- **Real-world examples** - Common use cases
- **Error handling** - Troubleshooting guides
- **Performance tips** - Rate limiting and optimization
- **Security considerations** - Authentication and permissions

## 🔗 External Resources

- [Official Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Sheets API Reference](https://developers.google.com/sheets/api/reference/rest)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

## 📝 Usage Examples

### Basic Reading
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

service = build('sheets', 'v4', credentials=credentials)
result = service.spreadsheets().values().get(
    spreadsheetId='your-spreadsheet-id',
    range='Sheet1!A1:B10'
).execute()
```

### Batch Writing
```python
batch_data = [
    {'range': 'Sheet1!A1:B2', 'values': [['Hello', 'World'], ['Data', 'Row 2']]},
    {'range': 'Sheet1!D1:E2', 'values': [['More', 'Data'], ['Row', '3']]}
]

service.spreadsheets().values().batchUpdate(
    spreadsheetId='your-spreadsheet-id',
    body={'valueInputOption': 'USER_ENTERED', 'data': batch_data}
).execute()
```

### Complex Operations
```python
batch_request = {
    'requests': [
        {
            'updateCells': {
                'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 2, 'startColumnIndex': 0, 'endColumnIndex': 2},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': 'Hello'}}, {'userEnteredValue': {'stringValue': 'World'}}]}],
                'fields': 'userEnteredValue'
            }
        },
        {
            'insertDimension': {
                'range': {'sheetId': 0, 'dimension': 'ROWS', 'startIndex': 5, 'endIndex': 7},
                'inheritFromBefore': True
            }
        }
    ]
}

service.spreadsheets().batchUpdate(
    spreadsheetId='your-spreadsheet-id',
    body=batch_request
).execute()
```

---

*This documentation is based on the official Google Sheets API v4 discovery document and covers all aspects of the API for comprehensive reference. Each file is designed to be self-contained while providing cross-references to related topics.* 