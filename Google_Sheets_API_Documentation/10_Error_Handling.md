# Google Sheets API v4 - Error Handling

## 📋 Overview

This document covers error handling for the Google Sheets API v4, including error codes, response formats, and troubleshooting strategies.

## 🚨 Common Error Responses

### 400 Bad Request
```json
{
  "error": {
    "code": 400,
    "message": "Invalid range",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "field": "range",
            "description": "Invalid A1 notation"
          }
        ]
      }
    ]
  }
}
```

### 401 Unauthorized
```json
{
  "error": {
    "code": 401,
    "message": "Request had invalid authentication credentials",
    "status": "UNAUTHENTICATED"
  }
}
```

### 403 Forbidden
```json
{
  "error": {
    "code": 403,
    "message": "The caller does not have permission",
    "status": "PERMISSION_DENIED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT"
      }
    ]
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "code": 404,
    "message": "Requested entity was not found",
    "status": "NOT_FOUND",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "SPREADSHEET_NOT_FOUND"
      }
    ]
  }
}
```

### 429 Too Many Requests
```json
{
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota group 'ReadGroup' and limit 'Read requests per minute per user' of service 'sheets.googleapis.com'",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "subject": "quota_exceeded",
            "description": "Rate limit exceeded"
          }
        ]
      }
    ]
  }
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "code": 500,
    "message": "Internal error encountered",
    "status": "INTERNAL"
  }
}
```

### 503 Service Unavailable
```json
{
  "error": {
    "code": 503,
    "message": "The service is currently unavailable",
    "status": "UNAVAILABLE"
  }
}
```

## 📊 Error Codes Reference

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Google Sheets API Specific Errors

#### Authentication Errors
- `UNAUTHENTICATED` - Invalid or missing authentication credentials
- `ACCESS_TOKEN_SCOPE_INSUFFICIENT` - Token lacks required scopes
- `ACCESS_TOKEN_EXPIRED` - Token has expired

#### Permission Errors
- `PERMISSION_DENIED` - User lacks permission for the operation
- `SPREADSHEET_NOT_FOUND` - Spreadsheet doesn't exist or is inaccessible
- `SHEET_NOT_FOUND` - Sheet doesn't exist in the spreadsheet

#### Validation Errors
- `INVALID_ARGUMENT` - Invalid parameter values
- `INVALID_RANGE` - Invalid A1 notation or range
- `INVALID_VALUE` - Invalid cell value or format
- `INVALID_DIMENSION` - Invalid row/column operations

#### Resource Errors
- `RESOURCE_EXHAUSTED` - Rate limit or quota exceeded
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `ALREADY_EXISTS` - Resource already exists

## 🔍 Error Details

### Field Violations
```json
{
  "fieldViolations": [
    {
      "field": "range",
      "description": "Invalid A1 notation: 'Sheet1!A1:B'"
    },
    {
      "field": "valueInputOption",
      "description": "Invalid value: 'INVALID_OPTION'"
    }
  ]
}
```

### Quota Violations
```json
{
  "violations": [
    {
      "subject": "quota_exceeded",
      "description": "Rate limit exceeded: 300 requests per minute"
    }
  ]
}
```

### Resource Info
```json
{
  "resourceType": "spreadsheets",
  "resourceName": "spreadsheets/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
}
```

## 🛠️ Troubleshooting Guide

### Authentication Issues

#### Problem: 401 Unauthorized
**Solutions:**
1. Check if access token is valid and not expired
2. Verify the token has the correct scopes
3. Ensure proper authentication flow

```python
# Check token validity
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

credentials = Credentials(token=access_token)
if credentials.expired:
    credentials.refresh(Request())
```

#### Problem: 403 Forbidden
**Solutions:**
1. Verify the user has access to the spreadsheet
2. Check if the spreadsheet is shared with the user
3. Ensure the service account has proper permissions

```python
# Check spreadsheet permissions
service = build('sheets', 'v4', credentials=credentials)
try:
    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()
except HttpError as error:
    if error.resp.status == 403:
        print("Permission denied - check sharing settings")
```

### Range and Data Issues

#### Problem: Invalid Range
**Solutions:**
1. Verify A1 notation format
2. Check if sheet name exists
3. Ensure range is within sheet boundaries

```python
# Validate range format
import re

def validate_a1_range(range_str):
    pattern = r'^[A-Za-z]+[0-9]*:[A-Za-z]+[0-9]*$'
    return bool(re.match(pattern, range_str))

# Example usage
if not validate_a1_range("A1:B10"):
    print("Invalid range format")
```

#### Problem: Invalid Values
**Solutions:**
1. Check data types for cells
2. Verify formulas are valid
3. Ensure dates are in correct format

```python
# Validate cell values
def validate_cell_value(value):
    if isinstance(value, (int, float, str, bool)):
        return True
    elif isinstance(value, dict) and 'formulaValue' in value:
        return True
    return False
```

### Rate Limiting Issues

#### Problem: 429 Too Many Requests
**Solutions:**
1. Implement exponential backoff
2. Use batch operations
3. Monitor quota usage

```python
import time
from googleapiclient.errors import HttpError

def make_request_with_backoff(service, request_func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return request_func()
        except HttpError as error:
            if error.resp.status == 429:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise error
    raise Exception("Max retries exceeded")
```

### Network Issues

#### Problem: Connection Timeout
**Solutions:**
1. Increase timeout values
2. Implement retry logic
3. Check network connectivity

```python
from googleapiclient.http import HttpRequest

# Set longer timeout
request = HttpRequest(
    url=url,
    method='GET',
    timeout=60  # 60 seconds timeout
)
```

## 📈 Monitoring and Logging

### Error Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_api_error(error):
    logger.error(f"API Error: {error.resp.status} - {error.content}")
    
    if error.resp.status == 429:
        logger.warning("Rate limit exceeded")
    elif error.resp.status == 403:
        logger.error("Permission denied")
    elif error.resp.status == 404:
        logger.error("Resource not found")
```

### Quota Monitoring
```python
def check_quota_headers(response):
    quota_remaining = response.headers.get('X-RateLimit-Remaining')
    quota_reset = response.headers.get('X-RateLimit-Reset')
    
    if quota_remaining:
        print(f"Quota remaining: {quota_remaining}")
    if quota_reset:
        print(f"Quota resets at: {quota_reset}")
```

## 🔧 Best Practices

### 1. Always Handle Errors
```python
try:
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
except HttpError as error:
    handle_api_error(error)
```

### 2. Implement Retry Logic
```python
def retry_on_error(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except HttpError as error:
            if error.resp.status in [429, 500, 503] and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise error
```

### 3. Validate Inputs
```python
def validate_spreadsheet_id(spreadsheet_id):
    if not spreadsheet_id or len(spreadsheet_id) < 10:
        raise ValueError("Invalid spreadsheet ID")
    return spreadsheet_id
```

### 4. Use Batch Operations
```python
# Instead of multiple individual requests
batch_request = {
    'valueInputOption': 'USER_ENTERED',
    'data': [
        {'range': 'Sheet1!A1:B2', 'values': [['A1', 'B1'], ['A2', 'B2']]},
        {'range': 'Sheet1!D1:E2', 'values': [['D1', 'E1'], ['D2', 'E2']]}
    ]
}
```

## 🔗 Related Documentation

- **[API Overview](01_API_Overview.md)** - Basic API information
- **[Rate Limits](11_Rate_Limits.md)** - Detailed quota information
- **[Request Examples](13_Request_Examples.md)** - Common request patterns
- **[Endpoints Reference](02_Endpoints_Reference.md)** - All API endpoints 