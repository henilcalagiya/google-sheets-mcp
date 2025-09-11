# Google Sheets MCP Server

> Powerful tools for automating Google Sheets using Model Context Protocol (MCP)

**mcp-name: io.github.henilcalagiya/google-sheets-mcp**

## Overview

Google Sheets MCP Server provides seamless integration of Google Sheets with any MCP-compatible client. It enables full spreadsheet automation — including creating, reading, updating, and deleting sheets — through a simple and secure API layer.

## Features

- Full CRUD support for Google Sheets and tables
- Works with Continue.dev, Claude Desktop, Perplexity, and other MCP clients
- Secure authentication via Google Service Account
- Comprehensive tools for Google Sheets automation
- Automatic installation via `uvx`

## Requirements

- Python 3.10+
- `uv` package manager (for `uvx` command)
- A Google Cloud project with a Service Account
- MCP-compatible client (e.g., Continue.dev)

**Install uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

---

## Quick Start

### 1. Set Up Google Service Account

**Step 1: Create a Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "my-sheets-automation")
4. Click "Create"

**Step 2: Enable Required APIs**
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API" → Click → "Enable"
3. Search for "Google Drive API" → Click → "Enable"

**Step 3: Create Service Account**
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter service account name (e.g., "sheets-mcp-service")
4. Click "Create and Continue"
5. Skip role assignment → Click "Continue"
6. Click "Done"

**Step 4: Generate JSON Key**
1. Click on your new service account email
2. Go to "Keys" tab → "Add Key" → "Create new key"
3. Choose "JSON" format → Click "Create"
4. The JSON file will download automatically

**Step 5: Extract Required Values**
Open the downloaded JSON file and note these values:
- `project_id` (e.g., "my-sheets-automation-123456")
- `private_key_id` (e.g., "a4ae73111b11b2c3b07cc01006e71eb8230dfa29")
- `private_key` (the long private key starting with "-----BEGIN PRIVATE KEY-----")
- `client_email` (e.g., "sheets-mcp-service@my-sheets-automation-123456.iam.gserviceaccount.com")
- `client_id` (e.g., "113227823918217958816")
- `client_x509_cert_url` (e.g., "https://www.googleapis.com/robot/v1/metadata/x509/sheets-mcp-service%40my-sheets-automation-123456.iam.gserviceaccount.com")

**Example Google service account JSON structure:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service%40your-project.iam.gserviceaccount.com"
}
```

[Follow this guide if needed](https://console.cloud.google.com/apis/credentials)

### 2. Configure MCP Client

```json
{
  "mcpServers": {
    "google-sheets-mcp": {
      "command": "uvx",
      "args": ["google-sheets-mcp@latest"],
      "env": {
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service%40your-project.iam.gserviceaccount.com"
      }
    }
  }
}
```

**💡 Pro Tip:** You can copy the values directly from your Google service account JSON file. The field names in the JSON file are used exactly as they are - no changes needed!

**🔄 Backward Compatibility:** The server also supports the old `GOOGLE_` prefixed variable names (e.g., `GOOGLE_PROJECT_ID`) for existing configurations.

### 3. Share Your Google Sheet with the Service Account

- Open your target Google Spreadsheet in your web browser.
- Click the **Share** button.
- Enter the **service account email** (e.g., `your-service@your-project.iam.gserviceaccount.com`) and assign **Editor** access.
- Click **Send** to provide editor permissions.

**🎉 You're all set!** Your MCP client will automatically install and run the package when needed.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Henil C Alagiya**

- **GitHub**: [@henilcalagiya](https://github.com/henilcalagiya)
- **LinkedIn**: [Henil C Alagiya](https://www.linkedin.com/in/henilcalagiya/)

**Support & Contributions:**
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/henilcalagiya/google-sheets-mcp/issues)
- 💬 **Questions**: Reach out on [LinkedIn](https://www.linkedin.com/in/henilcalagiya/)
- 🤝 **Contributions**: Pull requests welcome! 