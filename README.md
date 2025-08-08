# Google Sheets MCP Server

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tools](https://img.shields.io/badge/Tools-25%20Available-brightgreen.svg)](https://github.com/henilcalagiya/google-sheets-mcp)

A Model Context Protocol (MCP) server that provides **25 powerful tools** for interacting with Google Sheets. Built with FastMCP framework for seamless AI integration.

**What is MCP?** Model Context Protocol enables AI assistants to access external tools and data sources. This server connects your AI tools (Claude, Continue, Perplexity) directly to Google Sheets for powerful automation.

**📋 License:** Apache License 2.0  
**🛠️ Available Tools:** 25 Google Sheets operations  
**🚀 Quick Setup:** 3 steps to get started

## 🚀 Quick Start (3 Steps)

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

**💡 Keep this file safe!** You'll need its path for the next step.

### Step 2: Download, Setup & Configure

#### **Where to Run These Commands:**
- **macOS/Linux**: Terminal app
- **Windows**: Command Prompt or PowerShell
- **VS Code**: Integrated terminal
- **Any IDE**: Built-in terminal

#### **Setup Commands:**

**For macOS/Linux:**
```bash
# Clone and setup
git clone https://github.com/henilcalagiya/google-sheets-mcp.git
cd google-sheets-mcp

# Install uv (if needed) and setup environment
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate && uv sync

# Run auto setup
python auto_setup.py
```

**For Windows:**
```cmd
# Clone and setup
git clone https://github.com/henilcalagiya/google-sheets-mcp.git
cd google-sheets-mcp

# Install uv (if needed) and setup environment
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
uv venv && .venv\Scripts\activate && uv sync

# Run auto setup
python auto_setup.py
```


### **What You'll Get:**

#### **1. Configuration File on Desktop:**
```
✅ Created google-sheets-mcp-config.json on your Desktop
📁 Location: ~/Desktop/google-sheets-mcp-config.json
```

#### **2. Complete JSON in Terminal:**
```
============================================================
📋 COPY THIS CONFIGURATION TO YOUR MCP CLIENT:
============================================================
{ /* Complete configuration with your credentials */ }
============================================================
📋 END OF CONFIGURATION
============================================================
```


### Step 3: Connect MCP Client

**Copy the configuration to your MCP client:**

**For Claude Desktop:**
1. Open Claude Desktop settings
2. Add the JSON configuration from your terminal or Desktop file
3. Restart Claude Desktop

**For Continue:**
1. Open Continue settings
2. Add the JSON configuration from your terminal or Desktop file
3. Restart Continue

**For Perplexity:**
1. Open Perplexity settings
2. Go to the "Connectors" section to connect the MCP
3. Add the JSON configuration from your terminal or Desktop file
4. Restart Perplexity

**For other MCP clients:**
1. Find your client's MCP configuration section
2. Add the JSON configuration from your terminal or Desktop file
3. Restart your MCP client

**Share your Google Sheets:**
- **Email:** Use the service account email shown in your terminal. You can also find this email in the Google Cloud Console where you created the API, or in the JSON file that was created on your Desktop.
- **Permissions:** Give "Editor" access to your Google Sheets

**🎉 You're all set!** Start using all 25 Google Sheets tools in your MCP client.

## 📦 What's Included

### **🎯 Complete Setup Package:**
- **✅ Configuration file** on your Desktop
- **✅ Complete JSON** in terminal for easy copying
- **✅ 25 Google Sheets tools** ready to use
- **✅ Cross-platform support** (macOS, Linux, Windows)

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

#### UV Not Found
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

#### Missing Environment Variables
- The auto-setup script sets environment variables automatically.
- Ensure you have successfully run:
  ```bash
  python auto_setup.py
  ```

#### Cannot Access Google Sheets
- Share your Google Sheets with the service account email.
- Grant "Editor" permissions.

#### Authentication Failed
- Confirm that required APIs are enabled in the Google Cloud Console.
- Verify the service account has the necessary permissions.

### Testing Your Setup

- The auto-setup script validates your configuration automatically.
- No additional testing is required on any platform.

- **macOS/Linux:**
  ```bash
  # No additional testing needed
  ```
- **Windows:**
  ```cmd
  REM No additional testing needed
  ```

## 📁 Project Structure

```
gsheet-mcp-server/
├── gsheet_mcp_server/          # Main server code
│   ├── server.py               # Main server file (all tools)
│   ├── handler/                # Tool handlers
│   │   ├── spreadsheet/        # Spreadsheet operations
│   │   ├── sheets/            # Sheet operations
│   │   └── tables/            # Table operations
│   └── helper/                # Utility functions
├── auto_setup.py              # Automated setup script
├── pyproject.toml             # Project dependencies
├── uv.lock                    # Dependency lock file
└── README.md                  # This file
```

## 🔐 Security

- **Environment Variables:** Credentials stored securely in environment variables
- **No File Storage:** No credentials stored in files
- **Service Account:** Uses Google Service Account for secure API access
- **Minimal Permissions:** Only necessary Google Sheets and Drive permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request



## 📋 Example Configuration

Here's what your configuration will look like (automatically generated by `auto_setup.py`):

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "/Users/henil/.local/bin/uv",
      "args": [
        "run",
        "--project",
        "/Users/henil/Desktop/google-sheets-mcp",
        "python",
        "-m",
        "gsheet_mcp_server"
      ],
      "env": {
        "GOOGLE_PROJECT_ID": "my-awesome-project-123",
        "GOOGLE_PRIVATE_KEY_ID": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
        "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCq1LyRiC9OgKdO\nSfmJrrJ1Vs8nU/Vlq2Lpe5AtCzPZZLs0/hSTuIbIoB4MLwFn6xk4DsvzmUHtuvnI\n7JS5TSc2nZE/ln8+AEKZTzl+B/WjHWEVQxxC+Y9c+RgYRb7p42ZeiEV9RB33RNsr\ne4q11f1+Qqih+8U/d7Bt7ZLog6HmxBgbkQpnzowqUTQV5G9n2CMgvUWUzqqT986F\naNHDv3tu98cAg3bcXBvQSl0aDF7INlHqgjsKv0TRdXSgqMJUUQsLu5LWTZVRvXT1\n8K5A/UMQUDE/rND+SYaarb4awL0s3vaRDObZW6HSHwiewkHY+QBcAcdL18csOLXh\n2LfRXmc7AgMBAAECggEACNm3uaxuTAEhTRwQoZXJ+A4rhInvh8Nr2OzlRC1V6O2Y\n+KhS0jZ0Lf+K4l6rKOV9b9Vu7mFqULFpVJ9GA63aun45yTG83fNYjzqjKhLWuS0U\nSZ7b49JQCusAc3m9dkcxxoJQTCZTEsyvjfX8BlpoUWflvyUkC/5Q0fPQQ58ibPYI\ni1UMMc+KWbdof+fofgFZ0Ca1ccnEHJWgu8O2rQkBx9E3Nxd7BoiAXpdnFBxLK/+x\nSmZkKG+3Gpbi2GoMGnd8DUSJgDcsu6NMDJ+HKK48FdxNQ6k8LEPaBneitq1R/3qf\nQJKU5Ido9hVJ1gK2G3Cy566MeVLf1TivyWAZP6kqcQKBgQD/VV7Y0/XzQpnq+QBo\nU+dzFN0klFNT2wzAqFOYo6/j5YxBj0i74Nihd0QTBj2xVNoCIODzcrYQaoQoXOoN\n15n/T1swfHDcc9/Ti7t/3ZLnbGpQ6fogVSbgm177S1FWA8F87okAh+2vYJJFpkmo\nTCfQbbqs/LmFumCrXhBfbFz4nQKBgQDrcapDG6WWfqVvvUn4yLYLTfI0b3ZfzoDJ\nUH7k45Da0d4LUXE8HwI+iSONFOipsGu5fp/6Za2hnGx8OHV6mccpF7qujgdTNirG\nHO7u78/ZdC6EgqCsXAWZHMcSlWQjtZd93THeiIlcoJQGaWLSidTh84Q8hlL+ex41\nAJTfkia7twKBgQDIGX9bLcFyAp/dJYbMO/UGmzMzl4o2DVTRJxlcZetSDnL8be3y\nTyN2ZqFSx3FRp82yHVItd5h3BQLNHwPOFUj6bJZqSRupqKWgg8FNU7fs5WnsP3Fm\nJVVycFDfXwc/AXKBFe8IG36KEoSPUOIoooYRMe055FUAGC/qHK14GtRBgQKBgQDP\n5JG+p87S0AksXSvP7QoxeSYAfts7RZAaMmWZngbt8JnrzIH74DWPGnC1xlyaWRkF\ntXV1GAr0xLZWCVRSaS6ebkF8mBSHuTCTtkCT4lTZYekhQGa3Spn21J5DHn5JubKG\nhKXgJReFHpUWBEAqP2ImEWwWNVVbN0M48caCkv54iQKBgAUNESHRCMI+xQIpQc74\niVpuZ3KedSeKeSuAM3MuKmQizVRmX9GDmeVXCxg8J3V4q2JG62wJ3VxG0ZuNnR19\nYE7CxBQjFJ9sypbAdzcxWT7/mKlQpeHQ7h91dulmlS2APo7FfFvB9Y/flOvdUXbZ\nQaPx7ndUTgsovSBCxC5k+vut\n-----END PRIVATE KEY-----\n",
        "GOOGLE_CLIENT_EMAIL": "my-service-account@my-awesome-project-123.iam.gserviceaccount.com",
        "GOOGLE_CLIENT_ID": "123456789012345678901",
        "GOOGLE_AUTH_URI": "https://accounts.google.com/o/oauth2/auth",
        "GOOGLE_TOKEN_URI": "https://oauth2.googleapis.com/token",
        "GOOGLE_AUTH_PROVIDER_X509_CERT_URL": "https://www.googleapis.com/oauth2/v1/certs",
        "GOOGLE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/my-service-account%40my-awesome-project-123.iam.gserviceaccount.com"
      }
    }
  }
}
```



## 📄 License

Apache License 2.0 - see LICENSE file for details

## 🆘 Support

- **Issues:** Create an issue on [GitHub](https://github.com/henilcalagiya/google-sheets-mcp/issues)
- **Documentation:** Check the [Google Sheets API docs](https://developers.google.com/sheets/api)
- **MCP:** Review the [MCP documentation](https://modelcontextprotocol.io/)
- **Contact:** Reach out on [LinkedIn](https://www.linkedin.com/in/henilcalagiya/) for direct support

---

**Transform your Google Sheets experience with AI-powered automation! Start your journey in 3 simple steps above.** 🚀 