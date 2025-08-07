# Google Sheets MCP Server

A Model Context Protocol (MCP) server that provides **23 powerful tools** for interacting with Google Sheets. Built with FastMCP framework for seamless AI integration.

## 🚀 Quick Start (3 Steps)

### Step 1: Get Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Sheets API** and **Google Drive API**
4. Create a **Service Account** (recommended)
5. Download the credentials JSON file

### Step 2: Download & Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/gsheet-mcp-server.git
cd gsheet-mcp-server

# Run the automatic setup (installs UV and dependencies)
chmod +x setup.sh
./setup.sh
```

### Step 3: Configure & Use
```bash
# Option 1: Super simple auto-setup (recommended for non-technical users)
python3 auto_setup.py

# Option 2: Use the helper script
python3 setup_config.py

# Option 3: Manual setup
cp mcp_config_template.json mcp_config.json
# Edit mcp_config.json with your Google credentials

# Test the server
python3 test_server.py

# Add the JSON config to your MCP client and start using!
```

## 🎯 For Non-Technical Users

**Want the simplest possible setup?** Use the auto-setup script:

```bash
python3 auto_setup.py
```

This script will:
- ✅ Ask for your Google credentials JSON file
- ✅ Extract all the necessary information automatically
- ✅ Create the configuration file for you
- ✅ Test everything to make sure it works
- ✅ Give you the exact steps to use it

**See [ONE_CLICK_SETUP.md](ONE_CLICK_SETUP.md) for detailed non-technical instructions.**

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

## 🔧 Detailed Setup Instructions

### **Prerequisites:**
- Python 3.8+ 
- Google Cloud Project with APIs enabled
- Google Service Account credentials

### **Step-by-Step Setup:**

#### **1. Google Cloud Setup**
```bash
# 1. Go to Google Cloud Console
# 2. Create/select a project
# 3. Enable APIs:
#    - Google Sheets API
#    - Google Drive API
# 4. Create Service Account:
#    - Go to "IAM & Admin" > "Service Accounts"
#    - Click "Create Service Account"
#    - Download JSON credentials file
```

#### **2. Download & Install**
```bash
# Clone the repository
git clone https://github.com/yourusername/gsheet-mcp-server.git
cd gsheet-mcp-server

# Run automatic setup
chmod +x setup.sh
./setup.sh
```

#### **3. Configure Credentials**
```bash
# Option 1: Use the helper script (recommended)
python3 setup_config.py

# Option 2: Manual setup
cp mcp_config_template.json mcp_config.json
# Edit the file with your Google credentials
# See CREDENTIALS_SETUP.md for detailed instructions
nano mcp_config.json
# or use your preferred editor: code mcp_config.json, vim mcp_config.json, etc.
```

#### **4. Configure MCP Client**

**For Claude Desktop:**
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["run", "python", "-m", "gsheet_mcp_server"],
      "cwd": "/path/to/your/gsheet-mcp-server",
      "env": {
        "GOOGLE_PROJECT_ID": "your-project-id-here",
        "GOOGLE_PRIVATE_KEY_ID": "your-private-key-id-here",
        "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT_HERE\n-----END PRIVATE KEY-----\n",
        "GOOGLE_CLIENT_EMAIL": "your-service-account@your-project.iam.gserviceaccount.com",
        "GOOGLE_CLIENT_ID": "your-client-id-here",
        "GOOGLE_AUTH_URI": "https://accounts.google.com/o/oauth2/auth",
        "GOOGLE_TOKEN_URI": "https://oauth2.googleapis.com/token",
        "GOOGLE_AUTH_PROVIDER_X509_CERT_URL": "https://www.googleapis.com/oauth2/v1/certs",
        "GOOGLE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
      }
    }
  }
}
```

**For Continue:**
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["run", "python", "-m", "gsheet_mcp_server"],
      "cwd": "/path/to/your/gsheet-mcp-server"
    }
  }
}
```

**📝 How to get your credentials:**

Your Google credentials JSON file looks like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-123456",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project-123456.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-123456.iam.gserviceaccount.com"
}
```

Copy values from these fields:
- `project_id` → `GOOGLE_PROJECT_ID`
- `private_key_id` → `GOOGLE_PRIVATE_KEY_ID`
- `private_key` → `GOOGLE_PRIVATE_KEY`
- `client_email` → `GOOGLE_CLIENT_EMAIL`
- `client_id` → `GOOGLE_CLIENT_ID`
- `client_x509_cert_url` → `GOOGLE_CLIENT_X509_CERT_URL`

Then replace the placeholder values in the MCP config JSON above and update the `cwd` path to your actual project directory.

#### **5. Share Google Sheets**
```bash
# Share your Google Sheets with your service account email
# The email is in your credentials JSON file under "client_email"
# Give it "Editor" permissions
```

#### **6. Test & Use**
```bash
# Test the server
python3 test_server.py

# Start your MCP client and use all 23 tools!
```

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
# Check that all fields are filled in mcp_config.json
# See CREDENTIALS_SETUP.md for detailed instructions
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
```bash
# Test server startup
python3 test_server.py

# Expected output:
# ✅ Server started successfully (timed out as expected)
# 🎉 MCP server is working correctly!
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
├── setup.sh                   # Automatic setup script
├── setup_config.py            # Quick configuration setup script
├── mcp_config_template.json   # Template for MCP configuration
├── CREDENTIALS_SETUP.md       # Detailed credentials setup guide
├── test_server.py             # Server testing
├── mcp_config.json            # Your MCP client configuration (create from template)
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

- **[CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md)** - Detailed guide for setting up Google credentials
- **[SHARING_GUIDE.md](SHARING_GUIDE.md)** - How to share this server with others
- **[ENVIRONMENT_VARIABLES_SETUP.md](ENVIRONMENT_VARIABLES_SETUP.md)** - Environment variable setup details

## 📋 Complete Example Configuration

Here's a complete example of what your `mcp_config.json` should look like:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["run", "python", "-m", "gsheet_mcp_server"],
      "cwd": "/Users/yourusername/path/to/gsheet-mcp-server",
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
1. Copy the JSON above
2. Replace the credential values with your own
3. Update the `cwd` path to your project directory
4. Save as `mcp_config.json`

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues:** Create an issue on GitHub
- **Documentation:** Check the [Google Sheets API docs](https://developers.google.com/sheets/api)
- **MCP:** Review the [MCP documentation](https://modelcontextprotocol.io/)

---

**Ready to supercharge your Google Sheets workflow with AI? Get started in 3 steps above!** 🚀 