# Google Sheets MCP Server

25 powerful tools for Google Sheets automation via MCP (Model Context Protocol).

## Quick Start

1. **Install**: `uvx google-sheets-mcp@latest`

2. **Configure MCP Client**:
```json
{
  "mcpServers": {
    "google-sheets-mcp": {
      "command": "uvx",
      "args": ["google-sheets-mcp@latest"],
      "env": {
        "GOOGLE_PROJECT_ID": "your-project-id",
        "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
        "GOOGLE_CLIENT_EMAIL": "your-service@your-project.iam.gserviceaccount.com"
      }
    }
  }
}
```

3. **Set up Google Service Account** and share your sheets with the service account email.

## Features

- Create, read, update, delete spreadsheets and tables
- Works with Continue.dev, Claude Desktop, Perplexity, and other MCP clients
- Secure authentication via Google service account
- 25 comprehensive Google Sheets tools

## Installation

```bash
# Using uvx (recommended)
uvx google-sheets-mcp@latest

# Using pip
pip install google-sheets-mcp

# Using uv
uv add google-sheets-mcp
```

## License

MIT License 