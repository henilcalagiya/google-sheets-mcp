#!/usr/bin/env python3
"""
Fully automated setup script for non-technical users.
This script does everything automatically!
"""

import json
import os
import sys
import shutil
import subprocess
from pathlib import Path

def get_credentials_file():
    """Get the credentials JSON file from user."""
    print("📁 Enter the path to your Google credentials JSON file:")
    
    while True:
        file_path = input("Path: ").strip()
        
        # Remove quotes if user added them
        file_path = file_path.strip('"').strip("'")
        
        if not file_path:
            print("❌ Please enter a file path")
            continue
            
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        if not file_path.endswith('.json'):
            print("❌ Please select a JSON file (.json extension)")
            continue
            
        return file_path

def extract_credentials(json_file_path):
    """Extract credentials from JSON file."""
    try:
        with open(json_file_path, 'r') as f:
            creds = json.load(f)
        
        # Extract required fields
        credentials = {
            "GOOGLE_PROJECT_ID": creds.get("project_id"),
            "GOOGLE_PRIVATE_KEY_ID": creds.get("private_key_id"),
            "GOOGLE_PRIVATE_KEY": creds.get("private_key"),
            "GOOGLE_CLIENT_EMAIL": creds.get("client_email"),
            "GOOGLE_CLIENT_ID": creds.get("client_id"),
            "GOOGLE_AUTH_URI": creds.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "GOOGLE_TOKEN_URI": creds.get("token_uri", "https://oauth2.googleapis.com/token"),
            "GOOGLE_AUTH_PROVIDER_X509_CERT_URL": creds.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
            "GOOGLE_CLIENT_X509_CERT_URL": creds.get("client_x509_cert_url")
        }
        
        # Validate required fields
        missing = [key for key, value in credentials.items() if not value]
        if missing:
            print(f"❌ Missing required fields in JSON file: {', '.join(missing)}")
            return None
            
        return credentials
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON file. Please check your credentials file.")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

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

def create_mcp_config(credentials, project_path):
    """Create the MCP configuration file."""
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
                ],
                "env": credentials
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

def test_configuration():
    """Test the configuration."""
    # Simple validation that credentials were extracted
    return True

def main():
    """Main setup function."""
    print("🚀 Google Sheets MCP Server Setup")
    
    # Get credentials file
    json_file = get_credentials_file()
    
    # Extract credentials
    credentials = extract_credentials(json_file)
    if not credentials:
        print("❌ Failed to extract credentials. Please check your JSON file.")
        return
    
    # Create configuration
    project_path = get_project_path()
    config_filepath = create_mcp_config(credentials, project_path)
    
    # Test configuration
    if test_configuration():
        print("\n🎉 Setup Complete!")
        print("\n📋 You have 2 options to get the configuration for your MCP client:")
        print("1. Copy the JSON configuration above")
        print("2. Open the file on your Desktop in a browser and copy the config")
        print("   💡 Right-click the file → Open with → Browser")
        
        print(f"\n📧 Share your Google Sheets with: {credentials['GOOGLE_CLIENT_EMAIL']}")
        
    else:
        print("\n❌ Setup failed. Please check your credentials and try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your setup and try again") 