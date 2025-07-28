#!/usr/bin/env python3
"""
Test example for the updated rename_sheets_tool that accepts sheet names instead of sheet IDs.
"""

import os
from gsheet_mcp_server.handler.rename_sheets_handler import rename_sheets_handler
from gsheet_mcp_server.server import _setup_google_services

def test_rename_sheets():
    """Test the rename sheets tool with sheet names."""
    
    # Setup Google services
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not credentials_path:
        print("❌ GOOGLE_CREDENTIALS_PATH not set")
        return
    
    try:
        sheets_service, drive_service = _setup_google_services(credentials_path)
        print("✅ Google services initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Google services: {e}")
        return
    
    # Sample spreadsheet name (replace with your actual spreadsheet name)
    spreadsheet_name = "Test Spreadsheet"  # Replace with your spreadsheet name
    
    print(f"\n🔄 Testing Rename Sheets Tool for spreadsheet: {spreadsheet_name}")
    print("=" * 70)
    
    # Test 1: Rename single sheet
    print("\n📋 Test 1: Rename Single Sheet")
    print("-" * 40)
    
    result = rename_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["Sheet1"],
        new_titles=["Summary"]
    )
    
    print("Result:", result)
    
    # Test 2: Rename multiple sheets
    print("\n📋 Test 2: Rename Multiple Sheets")
    print("-" * 40)
    
    result = rename_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["Sheet1", "Data", "Temp"],
        new_titles=["Summary", "Analysis", "Backup"]
    )
    
    print("Result:", result)
    
    # Test 3: Error handling - non-existent sheet
    print("\n📋 Test 3: Error Handling - Non-existent Sheet")
    print("-" * 40)
    
    result = rename_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["NonExistentSheet"],
        new_titles=["NewName"]
    )
    
    print("Result:", result)
    
    # Test 4: Error handling - mismatched arrays
    print("\n📋 Test 4: Error Handling - Mismatched Arrays")
    print("-" * 40)
    
    result = rename_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["Sheet1", "Data"],
        new_titles=["Summary"]  # Only one title for two sheets
    )
    
    print("Result:", result)
    
    # Test 5: Error handling - empty input
    print("\n📋 Test 5: Error Handling - Empty Input")
    print("-" * 40)
    
    result = rename_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=[],
        new_titles=[]
    )
    
    print("Result:", result)
    
    print("\n" + "=" * 70)
    print("🎯 Rename sheets test completed!")

if __name__ == "__main__":
    test_rename_sheets() 