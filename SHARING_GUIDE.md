# 📤 Sharing Your Google Sheets MCP Server

## 🎯 Sharing Options

### **Option 1: Share the ZIP Package (Recommended)**
```bash
# Share this file:
gsheet-mcp-server.zip
```

**What's included:**
- ✅ Complete server code
- ✅ All dependencies (pyproject.toml, uv.lock)
- ✅ Helper scripts (update_mcp_config.py)
- ✅ Documentation (README.md, SETUP.md)
- ✅ Setup scripts (setup.sh, setup.bat)
- ✅ Template config (mcp_config_template.json)

**What's NOT included:**
- ❌ Your personal credentials
- ❌ Virtual environment (.venv/)
- ❌ Git history (.git/)
- ❌ Cache files (__pycache__/)

### **Option 2: Share the Folder Directly**
```bash
# Copy these files/folders:
gsheet_mcp_server/
pyproject.toml
uv.lock
mcp_config_template.json
update_mcp_config.py
extract_credentials_to_env.py
README.md
SETUP.md
ENVIRONMENT_VARIABLES_SETUP.md
MCP_CONFIG_SETUP.md
test_server.py
```

## 📋 Instructions for Recipients

### **Step 1: Extract and Setup**
```bash
# Extract the ZIP file
unzip gsheet-mcp-server.zip
cd gsheet-mcp-server

# Run automatic setup
chmod +x setup.sh
./setup.sh
```

### **Step 2: Get Google Credentials**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API and Google Drive API
4. Create a service account
5. Download JSON credentials file

### **Step 3: Configure the Server**
```bash
# Extract credentials to config
python3 update_mcp_config.py path/to/your/credentials.json
```

### **Step 4: Use with MCP Client**
1. Add the server to your MCP client config
2. Use the generated `mcp_config.json`
3. Start your MCP client
4. Use all 23 Google Sheets tools!

## 🚀 Quick Start for Recipients

```bash
# 1. Extract the package
unzip gsheet-mcp-server.zip
cd gsheet-mcp-server

# 2. Run setup
./setup.sh

# 3. Configure with your credentials
python3 update_mcp_config.py your-credentials.json

# 4. Use with your MCP client!
```

## 📦 Package Contents

```
gsheet-mcp-server/
├── gsheet_mcp_server/          # Main server code
├── pyproject.toml              # Dependencies
├── uv.lock                     # Locked versions
├── mcp_config_template.json    # Template config
├── update_mcp_config.py        # Helper script
├── extract_credentials_to_env.py # Env extraction
├── test_server.py              # Test script
├── setup.sh                    # Linux/Mac setup
├── setup.bat                   # Windows setup
├── QUICK_START.md             # Quick start guide
├── README.md                   # Main documentation
├── SETUP.md                    # Detailed setup
├── ENVIRONMENT_VARIABLES_SETUP.md # Env vars guide
└── MCP_CONFIG_SETUP.md        # MCP config guide
```

## 🔒 Security Notes

### **✅ Safe to Share:**
- Server code (no credentials)
- Template files
- Documentation
- Helper scripts

### **❌ Never Share:**
- `mcp_config.json` (contains real credentials)
- Your credentials JSON file
- `.venv/` folder
- Any files with real API keys

## 📤 Distribution Methods

### **Method 1: Email/File Sharing**
- Share the ZIP file directly
- Recipients extract and follow setup guide

### **Method 2: GitHub Repository**
```bash
# Create a clean repo (without credentials)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/gsheet-mcp-server.git
git push -u origin main
```

### **Method 3: Package Manager (Future)**
```bash
# Future: Publish to PyPI
pip install gsheet-mcp-server
```

## 🎉 Benefits of the ZIP Package

1. **Self-contained** - Everything needed is included
2. **Cross-platform** - Works on Windows, Mac, Linux
3. **Easy setup** - Automated installation scripts
4. **Complete documentation** - All guides included
5. **Secure** - No credentials included
6. **Small size** - Only 0.1 MB

**Your server is now ready to share!** 🚀 