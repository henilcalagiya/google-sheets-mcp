# MCP Setup Guide for Google Sheets Server

## 🚀 Setup Instructions

### **For Claude Desktop**

1. **Open Claude Desktop**
2. **Go to Settings** (gear icon)
3. **Find MCP Configuration** section
4. **Copy and paste** one of the configuration files below
5. **Restart Claude Desktop**
6. **Test the connection**

## 📋 Available Configuration Files

### **1. FastMCP Server (Recommended)**
Use `mcp_config.json` for the main server with structured output.

### **2. Legacy Server**
Use `mcp_config_legacy.json` for the original low-level implementation.

### **3. Cursor AI Configuration**
Use `mcp_config_cursor.json` for Cursor AI specific setup.

## 🛠 Available Tools

### **Basic Tools**
- **`list_spreadsheets`** - List all accessible Google Sheets
- **`list_sheets_in_spreadsheet`** - List all sheets in a specific spreadsheet
- **`read_sheet`** - Read data from a specific sheet
- **`write_sheet`** - Write data to a specific sheet
- **`create_spreadsheet`** - Create a new spreadsheet
- **`search_sheets`** - Search for content within spreadsheets



## 📊 Available Resources

- **`greeting://{name}`** - Personalized greetings
- **`spreadsheet://{spreadsheet_id}`** - Spreadsheet information


## 📝 Available Prompts

- **`analyze_spreadsheet`** - Analysis prompts
- **`create_report`** - Report generation prompts


## 🔧 Prerequisites

1. **Python 3.8+** installed
2. **Google Cloud Project** with Sheets API enabled
3. **Service Account** credentials JSON file
4. **Virtual Environment** activated

## 🧪 Testing

### **Test Server Connection**
```bash
# Test import
python -c "import gsheet_mcp_server.fastmcp_server; print('✅ Success')"

# Test execution
python -m gsheet_mcp_server.fastmcp_server

# Test with client
python examples/test_fastmcp_client.py
```

### **Test in Claude Desktop**
1. **Ask**: "List my Google Sheets"
2. **Ask**: "List sheets in spreadsheet [ID]"
3. **Ask**: "Read sheet [ID] Sheet1!A1:Z10"

## 🚨 Troubleshooting

### **Common Issues**

1. **"Command not found"**
   - Check Python path in configuration
   - Verify virtual environment is activated

2. **"Module not found"**
   - Install dependencies: `pip install -e .`
   - Check PYTHONPATH in configuration

3. **"Permission denied"**
   - Share Google Sheets with service account email
   - Check credentials file permissions

4. **"Connection timeout"**
   - Restart Claude Desktop
   - Check server is running

### **Debug Steps**

1. **Check logs** in Claude Desktop
2. **Test server manually** in terminal
3. **Verify credentials** are correct
4. **Check Google API** permissions

## 📁 Configuration Files

### **FastMCP Server Configuration**
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "/Users/henil/GSheetMCP Python/venv/bin/python3",
      "args": [
        "-m",
        "gsheet_mcp_server.fastmcp_server"
      ],
      "cwd": "/Users/henil/GSheetMCP Python",
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "/Users/henil/GSheetMCP Python/glossy-chimera-466301-c1-a4ae73111b11.json"
      }
    }
  }
}
```

### **Advanced Server Configuration**
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "/Users/henil/GSheetMCP Python/venv/bin/python3",
      "args": [
        "-m",
        "gsheet_mcp_server.advanced_server"
      ],
      "cwd": "/Users/henil/GSheetMCP Python",
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "/Users/henil/GSheetMCP Python/glossy-chimera-466301-c1-a4ae73111b11.json"
      }
    }
  }
}
```

## 🎯 Usage Examples

### **Basic Operations**
```
User: "List my Google Sheets"
AI: [Lists all accessible spreadsheets]

User: "List sheets in spreadsheet 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
AI: [Lists all sheets in that spreadsheet]

User: "Read sheet 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms Sheet1!A1:Z10"
AI: [Returns sheet data]
```



## 🔐 Security Notes

- **Never commit** credentials JSON files
- **Use service accounts** for server-to-server auth
- **Limit permissions** to minimum required
- **Rotate credentials** regularly

## 📞 Support

If you encounter issues:

1. **Check the logs** in Claude Desktop
2. **Test server manually** using the test client
3. **Verify Google API** setup and permissions
4. **Check configuration** file syntax 