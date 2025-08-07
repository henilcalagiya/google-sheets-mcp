#!/usr/bin/env python3
"""
Simple script to help users set up their MCP configuration.
"""

import os
import shutil
from pathlib import Path

def main():
    """Set up the MCP configuration template."""
    
    print("🚀 Setting up Google Sheets MCP Configuration...")
    
    # Check if template exists
    template_path = Path("mcp_config_template.json")
    if not template_path.exists():
        print("❌ Error: mcp_config_template.json not found!")
        print("💡 Make sure you're in the gsheet-mcp-server directory")
        return
    
    # Check if config already exists
    config_path = Path("mcp_config.json")
    if config_path.exists():
        print("⚠️  mcp_config.json already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("📝 Keeping existing mcp_config.json")
            print("💡 Edit it manually with your Google credentials")
            return
    
    # Copy template to config
    try:
        shutil.copy2(template_path, config_path)
        print("✅ Successfully copied mcp_config_template.json to mcp_config.json")
        print("")
        print("📝 Next steps:")
        print("1. Edit mcp_config.json with your Google credentials")
        print("2. See CREDENTIALS_SETUP.md for detailed instructions")
        print("3. Update the 'cwd' path to your actual project directory")
        print("4. Test with: python3 test_server.py")
        print("")
        print("💡 Quick edit commands:")
        print("   nano mcp_config.json")
        print("   code mcp_config.json")
        print("   vim mcp_config.json")
        
    except Exception as e:
        print(f"❌ Error copying template: {e}")

if __name__ == "__main__":
    main() 