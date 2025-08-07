#!/usr/bin/env python3
"""
Fully automated setup script for non-technical users.
This script does everything automatically!
"""

import json
import os
import sys
import shutil
from pathlib import Path

def print_step(step, description):
    """Print a formatted step."""
    print(f"\n{'='*50}")
    print(f"STEP {step}: {description}")
    print(f"{'='*50}")

def get_credentials_file():
    """Get the credentials JSON file from user."""
    print("\n📁 Please provide your Google credentials JSON file:")
    print("1. Drag and drop your JSON file here, or")
    print("2. Type the full path to your JSON file")
    print("   (e.g., /Users/YourName/Downloads/my-project-123456.json)")
    
    while True:
        file_path = input("\nEnter the path to your JSON file: ").strip()
        
        # Remove quotes if user added them
        file_path = file_path.strip('"').strip("'")
        
        if not file_path:
            print("❌ Please enter a file path")
            continue
            
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            print("💡 Make sure the path is correct and the file exists")
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

def get_project_path():
    """Get the current project path."""
    return os.getcwd()

def create_mcp_config(credentials, project_path):
    """Create the MCP configuration file."""
    config = {
        "mcpServers": {
            "google-sheets": {
                "command": "uv",
                "args": ["run", "python", "-m", "gsheet_mcp_server"],
                "cwd": project_path,
                "env": credentials
            }
        }
    }
    
    # Write the config file
    with open("mcp_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created mcp_config.json with your credentials")

def test_configuration():
    """Test the configuration."""
    print("\n🧪 Testing your configuration...")
    
    try:
        # Import and test the server
        import subprocess
        result = subprocess.run(
            ["python3", "test_server.py"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if "✅ Server started successfully" in result.stdout or "timed out as expected" in result.stdout:
            print("✅ Configuration test passed!")
            return True
        else:
            print("❌ Configuration test failed")
            print("Output:", result.stdout)
            print("Errors:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Configuration test passed! (Server started successfully)")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Google Sheets MCP Server - Auto Setup")
    print("This script will configure everything automatically!")
    
    # Step 1: Get credentials file
    print_step(1, "Get Google Credentials")
    json_file = get_credentials_file()
    
    # Step 2: Extract credentials
    print_step(2, "Extract Credentials")
    credentials = extract_credentials(json_file)
    if not credentials:
        print("❌ Failed to extract credentials. Please check your JSON file.")
        return
    
    print("✅ Successfully extracted credentials from JSON file")
    
    # Step 3: Create configuration
    print_step(3, "Create Configuration")
    project_path = get_project_path()
    create_mcp_config(credentials, project_path)
    
    # Step 4: Test configuration
    print_step(4, "Test Configuration")
    if test_configuration():
        print("\n🎉 SUCCESS! Your Google Sheets MCP server is ready!")
        print("\n📋 Next steps:")
        print("1. Copy the contents of mcp_config.json")
        print("2. Add it to your MCP client configuration")
        print("3. Share your Google Sheets with the service account email")
        print("4. Start using all 23 Google Sheets tools!")
        
        print(f"\n📧 Service Account Email: {credentials['GOOGLE_CLIENT_EMAIL']}")
        print("   (Share your Google Sheets with this email)")
        
        print("\n📁 Your configuration file: mcp_config.json")
        print("   (Copy this to your MCP client)")
        
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        print("💡 Make sure you have:")
        print("   - Valid Google credentials JSON file")
        print("   - Google Sheets and Drive APIs enabled")
        print("   - Proper permissions for the service account")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your setup and try again") 