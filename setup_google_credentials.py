#!/usr/bin/env python3
"""Setup script for Google API credentials."""

import json
import os
import sys
from pathlib import Path


def setup_service_account():
    """Guide user through setting up a service account."""
    print("=== Google Service Account Setup ===\n")
    
    print("1. Go to the Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Sheets API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Sheets API' and enable it")
    print("4. Create a service account:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'Service Account'")
    print("   - Fill in the details and create the account")
    print("5. Create a key for the service account:")
    print("   - Click on the service account you just created")
    print("   - Go to the 'Keys' tab")
    print("   - Click 'Add Key' > 'Create New Key'")
    print("   - Choose JSON format and download the file")
    print("6. Share your Google Sheets with the service account email")
    print("   (found in the JSON file under 'client_email')")
    
    credentials_path = input("\nEnter the path to your downloaded JSON file: ").strip()
    
    if not Path(credentials_path).exists():
        print(f"Error: File not found at {credentials_path}")
        return False
    
    # Test the credentials
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        if 'client_email' not in creds_data:
            print("Error: Invalid service account JSON file")
            return False
        
        print(f"\n✓ Service account email: {creds_data['client_email']}")
        print("Make sure to share your Google Sheets with this email address!")
        
        # Save the path to environment
        env_file = Path(".env")
        with open(env_file, "w") as f:
            f.write(f"GOOGLE_CREDENTIALS_PATH={credentials_path}\n")
        
        print(f"\n✓ Credentials path saved to {env_file}")
        return True
        
    except Exception as e:
        print(f"Error reading credentials file: {e}")
        return False


def setup_oauth2():
    """Guide user through setting up OAuth2 credentials."""
    print("=== Google OAuth2 Setup ===\n")
    
    print("1. Go to the Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Sheets API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Sheets API' and enable it")
    print("4. Create OAuth2 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Choose 'Desktop application'")
    print("   - Download the JSON file")
    print("5. Run the OAuth2 flow to get access tokens")
    
    credentials_path = input("\nEnter the path to your OAuth2 JSON file: ").strip()
    
    if not Path(credentials_path).exists():
        print(f"Error: File not found at {credentials_path}")
        return False
    
    # For OAuth2, you'll need to implement the flow to get tokens
    print("\nNote: OAuth2 setup requires additional implementation for token management.")
    print("For now, we recommend using a service account for easier setup.")
    
    return False


def main():
    """Main setup function."""
    print("Google Sheets MCP Server Setup\n")
    print("This script will help you set up Google API credentials for the MCP server.\n")
    
    print("Choose your authentication method:")
    print("1. Service Account (Recommended - easier to set up)")
    print("2. OAuth2 (More secure, requires user interaction)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        success = setup_service_account()
    elif choice == "2":
        success = setup_oauth2()
    else:
        print("Invalid choice. Please run the script again.")
        return
    
    if success:
        print("\n=== Setup Complete! ===")
        print("You can now run the MCP server with:")
        print("python -m gsheet_mcp_server")
        print("\nOr test it with:")
        print("python examples/test_client.py")
    else:
        print("\nSetup failed. Please check the errors above and try again.")


if __name__ == "__main__":
    main() 