# Google Sheets API v4 - Rate Limits

## 📋 Overview

This document covers rate limits, quotas, and best practices for managing API usage with the Google Sheets API v4.

## 📊 Standard Rate Limits

### Per-User Limits
- **Read requests:** 300 requests per minute per user
- **Write requests:** 60 requests per minute per user
- **Batch requests:** Count as single request
- **Developer metadata:** 100 requests per minute per user

### Per-Project Limits
- **Queries per day:** 1,000,000,000 requests per day
- **Queries per 100 seconds per user:** 300 requests
- **Queries per 100 seconds:** 1,000 requests

## 🔄 Quota Types

### 1. Read Quota
**Limit:** 300 requests per minute per user
**Applies to:**
- `GET /v4/spreadsheets/{spreadsheetId}`
- `GET /v4/spreadsheets/{spreadsheetId}/values/{range}`
- `GET /v4/spreadsheets/{spreadsheetId}/values:batchGet`
- `GET /v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}`

### 2. Write Quota
**Limit:** 60 requests per minute per user
**Applies to:**
- `PUT /v4/spreadsheets/{spreadsheetId}/values/{range}`
- `POST /v4/spreadsheets/{spreadsheetId}/values/{range}:append`
- `POST /v4/spreadsheets/{spreadsheetId}/values/{range}:clear`
- `POST /v4/spreadsheets/{spreadsheetId}/values:batchUpdate`
- `POST /v4/spreadsheets/{spreadsheetId}/values:batchClear`

### 3. Batch Quota
**Limit:** Counts as single request
**Applies to:**
- `POST /v4/spreadsheets/{spreadsheetId}:batchUpdate`

### 4. Developer Metadata Quota
**Limit:** 100 requests per minute per user
**Applies to:**
- `POST /v4/spreadsheets/{spreadsheetId}/developerMetadata:search`

## 🚨 Quota Exceeded Response

When you exceed the rate limits, you'll receive a 429 error:

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

## 📈 Monitoring Quota Usage

### Response Headers
The API includes quota information in response headers:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 245
X-RateLimit-Reset: 1640995200
```

### Checking Quota Programmatically
```python
import requests
from googleapiclient.discovery import build

def check_quota_usage(service, spreadsheet_id):
    try:
        response = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        # Check headers for quota info
        headers = response.get('headers', {})
        remaining = headers.get('X-RateLimit-Remaining')
        limit = headers.get('X-RateLimit-Limit')
        
        if remaining and limit:
            usage_percent = (int(limit) - int(remaining)) / int(limit) * 100
            print(f"Quota usage: {usage_percent:.1f}%")
            
        return response
    except Exception as e:
        print(f"Error checking quota: {e}")
```

## 🛠️ Best Practices

### 1. Use Batch Operations
Instead of multiple individual requests, use batch operations:

```python
# ❌ Bad: Multiple individual requests
for i in range(100):
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'A{i+1}',
        valueInputOption='USER_ENTERED',
        body={'values': [[f'Value {i+1}']]}
    ).execute()

# ✅ Good: Single batch request
batch_data = []
for i in range(100):
    batch_data.append({
        'range': f'A{i+1}',
        'values': [[f'Value {i+1}']]
    })

service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'valueInputOption': 'USER_ENTERED',
        'data': batch_data
    }
).execute()
```

### 2. Implement Exponential Backoff
```python
import time
import random
from googleapiclient.errors import HttpError

def make_request_with_backoff(service, request_func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return request_func()
        except HttpError as error:
            if error.resp.status == 429:
                # Calculate backoff time with jitter
                wait_time = min(2 ** attempt + random.uniform(0, 1), 60)
                print(f"Rate limited, waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise error
    
    raise Exception("Max retries exceeded")
```

### 3. Cache Responses
```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def get_spreadsheet_metadata(service, spreadsheet_id):
    """Cache spreadsheet metadata for 5 minutes"""
    return service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='properties,sheets.properties'
    ).execute()

# Use with cache invalidation
def get_cached_spreadsheet(service, spreadsheet_id):
    # Clear cache every 5 minutes
    if hasattr(get_spreadsheet_metadata, 'last_clear'):
        if time.time() - get_spreadsheet_metadata.last_clear > 300:
            get_spreadsheet_metadata.cache_clear()
            get_spreadsheet_metadata.last_clear = time.time()
    else:
        get_spreadsheet_metadata.last_clear = time.time()
    
    return get_spreadsheet_metadata(service, spreadsheet_id)
```

### 4. Monitor Usage Patterns
```python
import time
from collections import defaultdict

class QuotaMonitor:
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.last_reset = time.time()
    
    def track_request(self, endpoint):
        current_time = time.time()
        
        # Reset counters every minute
        if current_time - self.last_reset >= 60:
            self.request_counts.clear()
            self.last_reset = current_time
        
        self.request_counts[endpoint] += 1
        
        # Check limits
        if self.request_counts['read'] > 300:
            print("Warning: Approaching read quota limit")
        if self.request_counts['write'] > 60:
            print("Warning: Approaching write quota limit")
    
    def get_usage_stats(self):
        return dict(self.request_counts)

# Usage
monitor = QuotaMonitor()
monitor.track_request('read')
```

### 5. Optimize Request Frequency
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def batch_read_values(service, spreadsheet_id, ranges):
    """Read multiple ranges efficiently"""
    # Group ranges by sheet to minimize requests
    sheet_ranges = {}
    for range_name in ranges:
        sheet_name = range_name.split('!')[0]
        if sheet_name not in sheet_ranges:
            sheet_ranges[sheet_name] = []
        sheet_ranges[sheet_name].append(range_name)
    
    # Make batch requests
    results = []
    for sheet_name, sheet_ranges_list in sheet_ranges.items():
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=sheet_ranges_list
        ).execute()
        results.append(result)
    
    return results
```

## 📊 Quota Management Strategies

### 1. Request Queuing
```python
import queue
import threading
import time

class RequestQueue:
    def __init__(self, max_requests_per_minute=300):
        self.queue = queue.Queue()
        self.max_requests = max_requests_per_minute
        self.request_times = []
        self.lock = threading.Lock()
        
        # Start processing thread
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def add_request(self, request_func):
        self.queue.put(request_func)
    
    def _process_queue(self):
        while True:
            try:
                request_func = self.queue.get(timeout=1)
                
                # Check rate limit
                with self.lock:
                    current_time = time.time()
                    # Remove old requests (older than 1 minute)
                    self.request_times = [t for t in self.request_times 
                                        if current_time - t < 60]
                    
                    if len(self.request_times) >= self.max_requests:
                        # Wait until we can make another request
                        sleep_time = 60 - (current_time - self.request_times[0])
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                    
                    # Execute request
                    try:
                        result = request_func()
                        self.request_times.append(time.time())
                        print("Request successful")
                    except Exception as e:
                        print(f"Request failed: {e}")
                
            except queue.Empty:
                continue
```

### 2. Adaptive Rate Limiting
```python
class AdaptiveRateLimiter:
    def __init__(self, initial_rate=300):
        self.current_rate = initial_rate
        self.success_count = 0
        self.error_count = 0
        self.last_adjustment = time.time()
    
    def adjust_rate(self, success):
        current_time = time.time()
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        # Adjust rate every 100 requests
        if self.success_count + self.error_count >= 100:
            success_rate = self.success_count / (self.success_count + self.error_count)
            
            if success_rate > 0.95:
                # Increase rate if success rate is high
                self.current_rate = min(self.current_rate * 1.1, 300)
            elif success_rate < 0.8:
                # Decrease rate if success rate is low
                self.current_rate = max(self.current_rate * 0.9, 60)
            
            # Reset counters
            self.success_count = 0
            self.error_count = 0
            self.last_adjustment = current_time
    
    def get_delay(self):
        return 60 / self.current_rate
```

## 🔍 Monitoring Tools

### 1. Quota Dashboard
```python
import matplotlib.pyplot as plt
import pandas as pd

def create_quota_dashboard(usage_data):
    """Create a dashboard showing quota usage over time"""
    df = pd.DataFrame(usage_data)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot request counts
    ax1.plot(df['timestamp'], df['read_requests'], label='Read Requests')
    ax1.plot(df['timestamp'], df['write_requests'], label='Write Requests')
    ax1.axhline(y=300, color='r', linestyle='--', label='Read Limit')
    ax1.axhline(y=60, color='orange', linestyle='--', label='Write Limit')
    ax1.set_title('API Request Usage Over Time')
    ax1.set_ylabel('Requests per Minute')
    ax1.legend()
    
    # Plot success rate
    ax2.plot(df['timestamp'], df['success_rate'], label='Success Rate')
    ax2.axhline(y=0.95, color='g', linestyle='--', label='Target Success Rate')
    ax2.set_title('Request Success Rate')
    ax2.set_ylabel('Success Rate (%)')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
```

### 2. Alert System
```python
import smtplib
from email.mime.text import MIMEText

class QuotaAlert:
    def __init__(self, email_config):
        self.email_config = email_config
        self.alert_threshold = 0.8  # 80% of quota
    
    def check_and_alert(self, current_usage, limit):
        usage_percent = current_usage / limit
        
        if usage_percent > self.alert_threshold:
            self.send_alert(usage_percent, current_usage, limit)
    
    def send_alert(self, usage_percent, current_usage, limit):
        subject = f"Google Sheets API Quota Alert - {usage_percent:.1%} usage"
        body = f"""
        Quota Usage Alert:
        
        Current Usage: {current_usage}
        Limit: {limit}
        Usage Percentage: {usage_percent:.1%}
        
        Consider implementing rate limiting or batch operations.
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        
        # Send email (implement your email sending logic)
        print(f"Alert sent: {subject}")
```

## 🔗 Related Documentation

- **[API Overview](01_API_Overview.md)** - Basic API information
- **[Error Handling](10_Error_Handling.md)** - Error codes and troubleshooting
- **[Batch Operations](04_Batch_Operations.md)** - Efficient batch operations
- **[Request Examples](13_Request_Examples.md)** - Common request patterns 