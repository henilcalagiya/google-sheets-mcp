#!/usr/bin/env python3
"""
Minimal setup script for Google Sheets MCP Server.
This script creates a basic MCP configuration without credential handling.
Credentials will be provided by the MCP client during requests.
"""

import json
import os
import sys
import shutil
import subprocess
from pathlib import Path

def get_uv_path():
    """Get the uv executable path."""
    # Try to find uv in common locations
    possible_paths = [
        "/Users/henil/.local/bin/uv",  # Common uv installation path
        shutil.which("uv"),  # System PATH
        "/opt/homebrew/bin/uv",  # Homebrew installation
        "/usr/local/bin/uv",  # System installation
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    # If not found, try to run uv to get its path
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return shutil.which("uv")
    except:
        pass
    
    return "uv"  # Fallback to just "uv"

def get_project_path():
    """Get the current project path."""
    return os.getcwd()

def create_mcp_config(project_path):
    """Create the minimal MCP configuration file."""
    uv_path = get_uv_path()
    
    config = {
        "mcpServers": {
            "google-sheets": {
                "command": uv_path,
                "args": [
                    "run",
                    "--project",
                    project_path,
                    "python",
                    "-m",
                    "gsheet_mcp_server"
                ]
                # No env section - credentials will be provided by client
            }
        }
    }
    
    # Get desktop path
    desktop_path = os.path.expanduser("~/Desktop")
    config_filename = "google-sheets-mcp-config.json"
    config_filepath = os.path.join(desktop_path, config_filename)
    
    # Write the config file to desktop
    with open(config_filepath, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created {config_filename} on your Desktop")
    print(f"📁 Location: {config_filepath}")
    
    # Print the configuration for easy copying
    print("\n" + "="*60)
    print("📋 COPY THIS CONFIGURATION TO YOUR MCP CLIENT:")
    print("="*60)
    print(json.dumps(config, indent=2))
    print("="*60)
    print("📋 END OF CONFIGURATION")
    print("="*60)
    
    return config_filepath

def main():
    """Main setup function."""
    print("🚀 Google Sheets MCP Server Setup")
    print("📦 Minimal Configuration - No Credential Handling")
    print("💡 Credentials will be provided by your MCP client\n")
    
    # Create configuration
    project_path = get_project_path()
    config_filepath = create_mcp_config(project_path)
    
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Copy the JSON configuration above to your MCP client")
    print("2. Configure your MCP client to provide Google credentials")
    print("3. Share your Google Sheets with your service account email")
    print("\n💡 The server will receive credentials from your MCP client during requests")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your setup and try again") 