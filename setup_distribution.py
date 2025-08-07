#!/usr/bin/env python3
"""
Script to create a distributable package of the Google Sheets MCP Server.
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_distribution_package():
    """Create a distributable package."""
    
    # Create distribution directory
    dist_dir = "gsheet-mcp-server-dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Files to include
    files_to_copy = [
        "gsheet_mcp_server/",
        "pyproject.toml",
        "uv.lock",
        "mcp_config_template.json",
        "update_mcp_config.py",
        "extract_credentials_to_env.py",
        "README.md",
        "SETUP.md",
        "ENVIRONMENT_VARIABLES_SETUP.md",
        "MCP_CONFIG_SETUP.md",
        "test_server.py"
    ]
    
    # Files to exclude
    exclude_patterns = [
        "__pycache__",
        ".git",
        ".venv",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    print("📦 Creating distribution package...")
    
    # Copy files
    for item in files_to_copy:
        src = Path(item)
        dst = Path(dist_dir) / item
        
        if src.is_file():
            print(f"  📄 Copying {item}")
            shutil.copy2(src, dst)
        elif src.is_dir():
            print(f"  📁 Copying {item}")
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*exclude_patterns))
    
    # Create setup script
    setup_script = f"""#!/bin/bash
# Google Sheets MCP Server Setup Script

echo "🚀 Setting up Google Sheets MCP Server..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ UV installed successfully!"
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Get your Google credentials JSON file"
echo "2. Run: python3 update_mcp_config.py path/to/your/credentials.json"
echo "3. Configure your MCP client with mcp_config.json"
echo "4. Start your MCP client and use the Google Sheets tools!"
echo ""
echo "📖 For detailed instructions, see README.md"
"""
    
    with open(f"{dist_dir}/setup.sh", "w") as f:
        f.write(setup_script)
    
    # Make setup script executable
    os.chmod(f"{dist_dir}/setup.sh", 0o755)
    
    # Create Windows setup script
    setup_script_windows = f"""@echo off
REM Google Sheets MCP Server Setup Script

echo 🚀 Setting up Google Sheets MCP Server...

REM Check if UV is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ UV is not installed. Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo ✅ UV installed successfully!
)

REM Install dependencies
echo 📦 Installing dependencies...
uv sync

echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo 1. Get your Google credentials JSON file
echo 2. Run: python update_mcp_config.py path/to/your/credentials.json
echo 3. Configure your MCP client with mcp_config.json
echo 4. Start your MCP client and use the Google Sheets tools!
echo.
echo 📖 For detailed instructions, see README.md
pause
"""
    
    with open(f"{dist_dir}/setup.bat", "w") as f:
        f.write(setup_script_windows)
    
    # Create quick start guide
    quick_start = f"""# 🚀 Google Sheets MCP Server - Quick Start

## 📦 Installation

### Option 1: Automatic Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup
```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## 🔧 Configuration

1. **Get Google Credentials:**
   - Go to Google Cloud Console
   - Create a project and enable Google Sheets API
   - Create a service account and download JSON credentials

2. **Configure the Server:**
   ```bash
   python3 update_mcp_config.py path/to/your/credentials.json
   ```

3. **Configure MCP Client:**
   - Add the server to your MCP client config
   - Use the generated `mcp_config.json`

## 🎯 Usage

Start your MCP client and use the Google Sheets tools!

## 📖 Documentation

- `README.md` - Main documentation
- `SETUP.md` - Detailed setup guide
- `ENVIRONMENT_VARIABLES_SETUP.md` - Environment variables guide
- `MCP_CONFIG_SETUP.md` - MCP configuration guide

## 🆘 Troubleshooting

- **Missing dependencies:** Run `uv sync`
- **Authentication errors:** Check your Google credentials
- **MCP connection issues:** Verify your MCP client configuration
"""
    
    with open(f"{dist_dir}/QUICK_START.md", "w") as f:
        f.write(quick_start)
    
    # Create ZIP file
    zip_name = "gsheet-mcp-server.zip"
    print(f"📦 Creating {zip_name}...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(dist_dir)
    
    print(f"✅ Distribution package created: {zip_name}")
    print(f"📦 Package size: {os.path.getsize(zip_name) / 1024 / 1024:.1f} MB")
    
    return zip_name

if __name__ == "__main__":
    package_name = create_distribution_package()
    print(f"\n🎉 Distribution package ready: {package_name}")
    print("📤 Share this file with others!") 