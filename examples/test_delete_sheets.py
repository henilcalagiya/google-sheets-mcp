#!/usr/bin/env python3
"""
Test example for the updated delete_sheets_tool that accepts sheet names instead of sheet IDs.
"""

import os
from gsheet_mcp_server.handler.delete_sheets_handler import delete_sheets_handler
from gsheet_mcp_server.server import _setup_google_services

def test_delete_sheets():
    """Test the delete sheets tool with sheet names."""
    
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
    
    print(f"\n🗑️  Testing Delete Sheets Tool for spreadsheet: {spreadsheet_name}")
    print("=" * 70)
    
    # Test 1: Delete single sheet
    print("\n📋 Test 1: Delete Single Sheet")
    print("-" * 40)
    
    result = delete_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["TempSheet"]
    )
    
    print("Result:", result)
    
    # Test 2: Delete multiple sheets
    print("\n📋 Test 2: Delete Multiple Sheets")
    print("-" * 40)
    
    result = delete_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["OldData", "Backup", "Temp"]
    )
    
    print("Result:", result)
    
    # Test 3: Error handling - non-existent sheet
    print("\n📋 Test 3: Error Handling - Non-existent Sheet")
    print("-" * 40)
    
    result = delete_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["NonExistentSheet"]
    )
    
    print("Result:", result)
    
    # Test 4: Error handling - mixed valid/invalid sheets
    print("\n📋 Test 4: Error Handling - Mixed Valid/Invalid Sheets")
    print("-" * 40)
    
    result = delete_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=["Sheet1", "NonExistentSheet", "Data"]
    )
    
    print("Result:", result)
    
    # Test 5: Error handling - empty input
    print("\n📋 Test 5: Error Handling - Empty Input")
    print("-" * 40)
    
    result = delete_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_names=[]
    )
    
    print("Result:", result)
    
    # Test 6: Error handling - non-existent spreadsheet
    print("\n📋 Test 6: Error Handling - Non-existent Spreadsheet")
    print("-" * 40)
    
    result = delete_sheets_handler(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name="NonExistentSpreadsheet",
        sheet_names=["Sheet1"]
    )
    
    print("Result:", result)
    
    print("\n" + "=" * 70)
    print("🎯 Delete sheets test completed!")

if __name__ == "__main__":
    test_delete_sheets() 