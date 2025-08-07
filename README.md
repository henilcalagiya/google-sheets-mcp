# Google Sheets MCP Server

A Model Context Protocol (MCP) server that provides **23 powerful tools** for interacting with Google Sheets. Built with FastMCP framework for seamless AI integration.

## 🚀 Quick Start (2 Steps)

### Step 1: Get Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Sheets API** and **Google Drive API**
4. Create a **Service Account** (recommended)
5. Download the credentials JSON file

### Step 2: Download, Setup & Configure

#### **Where to Run These Commands:**
- **macOS/Linux**: Terminal app
- **Windows**: Command Prompt or PowerShell
- **VS Code**: Integrated terminal
- **Any IDE**: Built-in terminal

#### **Setup Commands:**

**For macOS/Linux:**
```bash
# Clone the repository
git clone https://github.com/yourusername/gsheet-mcp-server.git
cd gsheet-mcp-server

# Setup with uv (automatic dependency management)
uv venv
source .venv/bin/activate
uv sync

# Complete setup in one go
python auto_setup.py
```

**For Windows (Command Prompt):**
```cmd
# Clone the repository
git clone https://github.com/yourusername/gsheet-mcp-server.git
cd gsheet-mcp-server

# Setup with uv (automatic dependency management)
uv venv
.venv\Scripts\activate
uv sync

# Complete setup in one go
python auto_setup.py
```

**For Windows (PowerShell):**
```powershell
# Clone the repository
git clone https://github.com/yourusername/gsheet-mcp-server.git
cd gsheet-mcp-server

# Setup with uv (automatic dependency management)
uv venv
.venv\Scripts\Activate.ps1
uv sync

# Complete setup in one go
python auto_setup.py
```


### **What You'll Get:**

#### **1. Configuration File on Desktop:**
```
✅ Created google-sheets-mcp-config.json on your Desktop
📁 Location: /Users/henil/Desktop/google-sheets-mcp-config.json
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

#### **3. Clear Next Steps:**
```
📋 Next steps:
1. Copy the configuration above to your MCP client
2. Share your Google Sheets with the service account email
3. Start using all 23 Google Sheets tools!
```

**The auto-setup script handles everything automatically!**

## 📋 What You Get

### **23 Google Sheets Tools Available:**

#### **📊 Read Operations (8 tools):**
- List all spreadsheets
- List sheets in a spreadsheet
- Analyze sheet data
- Get table data and metadata
- Read table rows and cells
- Find specific table cells

#### **✏️ Write Operations (15 tools):**
- Create new spreadsheets and sheets
- Rename spreadsheets and sheets
- Delete sheets and spreadsheets
- Create and manage tables
- Insert, update, and delete table records
- Sort and clear table data
- Manage table columns and properties



## 🛠️ Available Tools

### **Spreadsheet Management:**
- `list_spreadsheets_and_sheets` - List all accessible spreadsheets
- `rename_spreadsheet` - Rename a spreadsheet

### **Sheet Operations:**
- `add_sheets_to_spreadsheet` - Add new sheets
- `delete_sheets_from_spreadsheet` - Delete sheets
- `duplicate_sheet` - Duplicate existing sheets
- `rename_sheets_in_spreadsheet` - Rename sheets
- `analyze_sheet` - Analyze sheet data and structure

### **Table Operations:**
- `create_table` - Create new tables
- `get_table_data` - Get table data
- `get_table_metadata` - Get table structure info
- `get_table_rows` - Get specific table rows
- `insert_table_records` - Add new records
- `update_table_row` - Update existing records
- `delete_table_records` - Delete records
- `clear_table_data` - Clear all table data
- `delete_table` - Delete entire table
- `rename_table` - Rename table
- `sort_table` - Sort table data
- `toggle_table_footer` - Show/hide table footer

### **Column Management:**
- `add_table_column` - Add new columns
- `delete_table_column` - Delete columns
- `rename_table_column` - Rename columns
- `change_table_column_type` - Change column data type
- `manage_column_properties` - Manage column settings
- `manage_dropdown_options` - Manage dropdown lists

### **Cell Operations:**
- `find_table_cells` - Find specific cells
- `update_table_cells` - Update cell values
- `get_table_data_by_columns` - Get data by specific columns

## 🔍 Troubleshooting

### **Common Issues:**

#### **"UV not found"**
```bash
# Install UV manually
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### **"Missing environment variables"**
```bash
# The auto-setup script handles this automatically
# Make sure you ran python auto_setup.py successfully
```

#### **"Cannot access Google Sheets"**
```bash
# Share your Google Sheets with service account email
# Give "Editor" permissions
```

#### **"Authentication failed"**
```bash
# Check that APIs are enabled in Google Cloud Console
# Verify service account has correct permissions
```

### **Testing Your Setup:**

**For macOS/Linux:**
```bash
# The auto-setup script validates everything automatically!
# No additional testing needed
```

**For Windows:**
```cmd
# The auto-setup script validates everything automatically!
# No additional testing needed
```

## 📁 Project Structure

```
gsheet-mcp-server/
├── gsheet_mcp_server/          # Main server code
│   ├── server.py               # Main server file (23 tools)
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

## 📚 Additional Documentation

- **Auto-setup script** - Handles all configuration automatically
- **Google Cloud Console** - For setting up credentials and APIs
- **MCP Documentation** - For understanding the protocol

## 📋 Complete Example Configuration

Here's a complete example of what your configuration should look like (automatically generated by `auto_setup.py`):

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

**💡 Quick Setup:**

**Complete setup in one go:**
1. Follow the Quick Start steps above
2. Run `python auto_setup.py` 
3. Copy the JSON configuration from terminal output
4. Add to your MCP client configuration
5. Share your Google Sheets with the service account email

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues:** Create an issue on GitHub
- **Documentation:** Check the [Google Sheets API docs](https://developers.google.com/sheets/api)
- **MCP:** Review the [MCP documentation](https://modelcontextprotocol.io/)

---

**Ready to supercharge your Google Sheets workflow with AI? Get started in 3 steps above!** 🚀 