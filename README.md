# Google Sheets MCP Server

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tools](https://img.shields.io/badge/Tools-25%20Available-brightgreen.svg)](https://github.com/henilcalagiya/google-sheets-mcp)
[![PyPI](https://img.shields.io/badge/PyPI-google--sheets--mcp-blue.svg)](https://pypi.org/project/google-sheets-mcp/)

Your AI Assistant's Gateway to Google Sheets! 📊

A Model Context Protocol (MCP) server that provides **25 powerful tools** for interacting with Google Sheets. Built with FastMCP framework for seamless AI integration.

**What is MCP?** Model Context Protocol enables AI assistants to access external tools and data sources. This server connects your AI tools (Claude, Continue, Perplexity) directly to Google Sheets for powerful automation.

**📋 License:** Apache License 2.0  
**🛠️ Available Tools:** 25 Google Sheets operations  
**🚀 Quick Setup:** One line to get started  
**🔐 Authentication:** Client-provided credentials (no environment variables needed)

## 🚀 Quick Start (One Line!)

### Step 1: Get Google Credentials

**Follow these steps to get your Google credentials JSON file:**

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create or Select a Project**
   - Click the project dropdown at the top left
   - Click **"New Project"** or select an existing project
   - If creating new: Enter a name and click **"Create"**

3. **Enable Required APIs**
   - In the left sidebar, click **"APIs & Services" > "Library"**
   - Search for **"Google Sheets API"** → Click → **"Enable"**
   - Search for **"Google Drive API"** → Click → **"Enable"**

4. **Create a Service Account**
   - Go to **"APIs & Services" > "Credentials"**
   - Click **"Create Credentials"** → **"Service account"**
   - Enter a name (e.g., `google-sheets-mcp`) → **"Create and Continue"**
   - Click **"Continue"** → **"Done"**

5. **Generate JSON Key**
   - In the service accounts list, click your new service account email
   - Go to **"Keys"** tab → **"Add Key"** → **"Create new key"**
   - Choose **"JSON"** → **"Create"**
   - The `.json` file will download automatically

**💡 Keep this file safe!** You'll need its contents for the next step.

### Step 2: Install & Run

#### **Option A: One-Line Execution (Recommended)**

```bash
# Install and run in one go
uvx google-sheets-mcp@latest
```

#### **Option B: Traditional Installation**

```bash
# Install the package
pip install google-sheets-mcp

# Run the server
python -m gsheet_mcp_server
```

#### **Option C: Manual Installation**

```bash
# Clone and setup
git clone https://github.com/henilcalagiya/google-sheets-mcp.git
cd google-sheets-mcp

# Install uv (if needed) and setup environment
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate && uv sync

# Run the server
python -m gsheet_mcp_server
```

### **What You'll Get:**

#### **✅ Server Running with 25 Tools**
```
🚀 Google Sheets MCP Server
📦 Package: google-sheets-mcp
🛠️ 25 powerful tools for Google Sheets automation
💡 Client Credentials Mode - No Environment Variables
==================================================
✅ Starting MCP server...
🔌 Ready to connect with MCP clients!
📋 Available tools: 25 Google Sheets operations
💡 Credentials will be provided by your MCP client during requests
==================================================
```

### Step 3: Configure MCP Client

**Configure your MCP client to provide Google credentials with each request.**

#### **For Continue.dev:**
1. Open Continue.dev
2. Go to Settings → MCP Servers
3. Add new server with this config:
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["google-sheets-mcp@latest"]
    }
  }
}
```

#### **For Claude Desktop:**
1. Open Claude Desktop
2. Go to Settings → MCP
3. Add the same configuration as above

#### **For Perplexity:**
1. Open Perplexity
2. Go to Settings → MCP Servers
3. Add the configuration

### Step 4: Share Your Google Sheets

**Share your Google Sheets with the service account email from your JSON file.**

**For example:**
- **Email:** `your-service@project.iam.gserviceaccount.com`
- **Permissions:** Give "Editor" access to your Google Sheets

**🎉 You're all set!** Start using all 25 Google Sheets tools in your MCP client.

## 📦 What's Included

### **🎯 Complete Setup Package:**
- **✅ 25 Google Sheets tools** ready to use
- **✅ Cross-platform support** (macOS, Linux, Windows)
- **✅ PyPI package** for easy installation
- **✅ One-line execution** with uvx
- **✅ Client-provided credentials** (no environment variables)

## 🛠️ Google Sheets Tools Overview

A total of **25 tools** are available, grouped by function. Each tool is listed with its operation and command name for easy reference.

### **📊 Spreadsheet Management (2 tools)**
- `discover_spreadsheets_tool` — List all accessible spreadsheets and their sheets
- `update_spreadsheet_title_tool` — Rename a spreadsheet

### **📋 Sheet Management (5 tools)**
- `create_sheets_tool` — Add new sheets to a spreadsheet
- `delete_sheets_tool` — Delete sheets from a spreadsheet
- `create_duplicate_sheet_tool` — Duplicate existing sheets
- `update_sheet_titles_tool` — Rename sheets in a spreadsheet
- `analyze_sheet_structure_tool` — Analyze sheet data and structure

### **📈 Table Management (18 tools)**

#### **Table CRUD Operations (4 tools)**
- `create_table_tool` — Create new tables with specified columns and data types
- `delete_table_tool` — Delete entire tables
- `update_table_title_tool` — Rename tables
- `get_table_metadata_tool` — Get comprehensive table structure and metadata

#### **Data Operations (4 tools)**
- `get_table_data_tool` — Get table data with optional filtering
- `add_table_records_tool` — Add new records to tables
- `delete_table_records_tool` — Delete specific records from tables
- `update_table_sorting_tool` — Sort table data by specific columns

#### **Column Operations (6 tools)**
- `add_table_column_tool` — Add new columns to existing tables
- `delete_table_column_tool` — Delete specific columns from tables
- `update_table_column_name_tool` — Update column names
- `update_table_column_type_tool` — Update column data types
- `update_dropdown_options_tool` — Update dropdown lists and options
- `get_sheet_cells_by_notation_tool` — Get values from specific cells using A1 notation

#### **Cell Operations (4 tools)**
- `update_table_cells_by_notation_tool` — Update specific cells using A1 notation
- `get_sheet_cells_by_range_tool` — Get cell data from specific ranges
- `update_table_cells_by_range_tool` — Update cell data in specific ranges
- `get_sheet_cells_by_notation_tool` — Get values from specific cells using A1 notation

**Note:** All tools are accessible after setup. Each tool provides comprehensive functionality for Google Sheets automation and management.

## 🔍 Troubleshooting

### Common Issues

#### UV Not Found (Manual Installation Only)
- **Install UV manually:**
  - **macOS/Linux:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
  - **Windows PowerShell:**
    ```powershell
    irm https://astral.sh/uv/install.ps1 | iex
    ```
  - **Windows Command Prompt:**
    ```cmd
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

#### Cannot Access Google Sheets
- Share your Google Sheets with the service account email.
- Grant "Editor" permissions.

#### Authentication Failed
- Confirm that required APIs are enabled in the Google Cloud Console.
- Verify the service account has the necessary permissions.

#### MCP Client Not Connecting
- Check MCP configuration in your client
- Verify server is running: `uvx google-sheets-mcp@latest`

### Testing Your Setup

- The server starts without requiring credentials
- Credentials are validated when tools are used
- No additional testing is required on any platform

## 📁 Project Structure

```
google-sheets-mcp/
├── gsheet_mcp_server/          # Main server code
│   ├── server.py               # Main server file (all tools)
│   ├── setup.py                # Setup script for PyPI users
│   ├── handler/                # Tool handlers
│   │   ├── spreadsheet/        # Spreadsheet operations
│   │   ├── sheets/            # Sheet operations
│   │   └── tables/            # Table operations
│   └── helper/                # Utility functions
├── __main__.py                 # Direct execution entry point
├── auto_setup.py              # Automated setup script (manual installation)
├── pyproject.toml             # Project dependencies
├── uv.lock                    # Dependency lock file
└── README.md                  # This file
```

## 🔐 Security

- **Client-Provided Credentials:** Credentials passed directly from MCP client
- **No File Storage:** No credentials stored in files or environment variables
- **Service Account:** Uses Google Service Account for secure API access
- **Minimal Permissions:** Only necessary Google Sheets and Drive permissions
- **On-Demand Authentication:** Credentials validated per request

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

Apache License 2.0 - see LICENSE file for details

## 🆘 Support

- **Issues:** Create an issue on [GitHub](https://github.com/henilcalagiya/google-sheets-mcp/issues)
- **Documentation:** Check the [Google Sheets API docs](https://developers.google.com/sheets/api)
- **MCP:** Review the [MCP documentation](https://modelcontextprotocol.io/)
- **Contact:** Reach out on [LinkedIn](https://www.linkedin.com/in/henilcalagiya/) for direct support

---

**Transform your Google Sheets experience with AI-powered automation! Start your journey in one line above.** 🚀 