# Google Sheets MCP Server

A Model Context Protocol (MCP) server that provides access to Google Sheets functionality using the FastMCP framework.

## Features

- **Tools**: Read and write data from Google Sheets, list spreadsheets, create new ones, search content
- **Resources**: Access spreadsheet information and personalized greetings
- **Prompts**: Generate analysis prompts and report templates
- **Structured Output**: Return validated, typed data using Pydantic models
- **Progress Reporting**: Real-time progress updates for long-running operations
- **Context Support**: Access to MCP capabilities through context objects
- **Completion Support**: Auto-completion for arguments and parameters
- **Elicitation**: Interactive user prompts for additional information

## Installation

1. **Clone this repository:**
   ```bash
   git clone <your-repo-url>
   cd gsheet-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set up Google Sheets API credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API and Google Drive API
   - Create credentials (Service Account recommended)
   - Download the credentials JSON file
   - Set the path: `export GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json`

## Quick Start

### Basic Server (FastMCP)

```bash
# Run the basic FastMCP server
python -m gsheet_mcp_server.fastmcp_server
```

### Legacy Server (Low-level)

```bash
# Run the original low-level server
python -m gsheet_mcp_server
```

## Available Tools

### Basic Tools
- **`list_spreadsheets`** - List all accessible Google Sheets with structured output
- **`list_sheets_in_spreadsheet`** - List all sheets in a specific spreadsheet
- **`read_sheet`** - Read data from a specific sheet
- **`write_sheet`** - Write data to a specific sheet  
- **`create_spreadsheet`** - Create a new spreadsheet
- **`search_sheets`** - Search for content within spreadsheets



## Available Resources

- **`greeting://{name}`** - Get a personalized greeting
- **`spreadsheet://{spreadsheet_id}`** - Get information about a specific spreadsheet


## Available Prompts

- **`analyze_spreadsheet`** - Generate prompts for analyzing spreadsheet data
- **`create_report`** - Generate prompts for creating reports


## Structured Output Examples

The server returns structured data using Pydantic models:

```python
# SpreadsheetInfo model
{
    "id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "name": "Sample Spreadsheet",
    "created_time": "2024-01-01T00:00:00.000Z",
    "modified_time": "2024-01-02T00:00:00.000Z",
    "url": "https://docs.google.com/spreadsheets/d/..."
}

# SearchResult model
{
    "spreadsheet": "Sample Spreadsheet",
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "sheet": "Sheet1",
    "cell": "A1",
    "value": "Sample Data"
}

# SheetInfo model
{
    "sheet_id": 0,
    "title": "Sheet1",
    "index": 0,
    "grid_properties": {
        "rowCount": 1000,
        "columnCount": 26
    }
}
```

## MCP Client Integration

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "gsheet": {
      "command": "python",
      "args": ["-m", "gsheet_mcp_server.fastmcp_server"],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "/path/to/credentials.json"
      }
    }
  }
}
```

## Development

### Using MCP Development Tools

```bash
# Install MCP CLI
pip install "mcp[cli]"

# Run server in development mode
mcp dev gsheet_mcp_server/fastmcp_server.py

# Add dependencies
mcp dev gsheet_mcp_server/fastmcp_server.py --with pandas --with numpy

# Mount local code
mcp dev gsheet_mcp_server/fastmcp_server.py --with-editable .
```

### Install in Claude Desktop

```bash
# Install the server
mcp install gsheet_mcp_server/fastmcp_server.py

# Custom name
mcp install gsheet_mcp_server/fastmcp_server.py --name "My Google Sheets Server"

# Environment variables
mcp install gsheet_mcp_server/fastmcp_server.py -v GOOGLE_CREDENTIALS_PATH=/path/to/creds.json
```

### Testing

```bash
# Test the server
python examples/test_client.py

# Run tests
pytest

# Format code
black .
isort .
```

## Server Capabilities

The server implements the following MCP capabilities:

| Capability | Feature Flag | Description |
|------------|--------------|-------------|
| tools | listChanged | Tool discovery and execution |
| resources | subscribe/listChanged | Resource exposure and updates |
| prompts | listChanged | Prompt template management |
| completions | - | Argument completion suggestions |
| logging | - | Server logging configuration |

## Architecture

### FastMCP vs Low-level

- **FastMCP**: High-level, decorator-based API (recommended)
- **Low-level**: Full protocol control, manual message handling

### Transport Options

- **stdio**: Standard input/output (default)
- **streamable-http**: HTTP-based transport for production
- **sse**: Server-Sent Events (deprecated)

## Security Best Practices

1. **Keep credentials secure**
   - Don't commit JSON files to version control
   - Use environment variables or secure secret management
   - Rotate credentials regularly

2. **Minimize permissions**
   - Only grant necessary permissions to service accounts
   - Use custom roles with specific permissions

3. **Monitor usage**
   - Set up billing alerts in Google Cloud Console
   - Monitor API usage and quotas

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Verify `GOOGLE_CREDENTIALS_PATH` environment variable
   - Check file permissions and path

2. **"Permission denied" errors**
   - Share Google Sheets with service account email
   - Verify API permissions in Google Cloud Console

3. **"API not enabled" errors**
   - Enable Google Sheets API and Google Drive API
   - Check project billing status

4. **Import errors**
   - Install dependencies: `pip install -e .`
   - Check Python version (3.8+ required)

### Getting Help

- Check the [Google Sheets API documentation](https://developers.google.com/sheets/api)
- Review the [MCP Python SDK documentation](https://github.com/modelcontextprotocol/python-sdk)
- Check server logs for detailed error messages

## License

MIT License 