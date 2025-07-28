#!/usr/bin/env python3
"""
Test example for the updated insert_rows tool that accepts sheet names instead of sheet IDs.
"""

import os
from gsheet_mcp_server.handler.insert_rows_handler import insert_rows_data
from gsheet_mcp_server.server import _setup_google_services

def test_insert_rows():
    """Test the insert rows tool with sheet names."""
    
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
    
    print(f"\n📝 Testing Insert Rows Tool for spreadsheet: {spreadsheet_name}")
    print("=" * 70)
    
    # Test 1: Insert single row
    print("\n📋 Test 1: Insert Single Row")
    print("-" * 40)
    
    result = insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name="Sheet1",
        start_index=5,
        end_index=6
    )
    
    print("Result:", result)
    
    # Test 2: Insert multiple rows
    print("\n📋 Test 2: Insert Multiple Rows")
    print("-" * 40)
    
    result = insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name="Data",
        start_index=10,
        end_index=13
    )
    
    print("Result:", result)
    
    # Test 3: Insert at beginning
    print("\n📋 Test 3: Insert at Beginning")
    print("-" * 40)
    
    result = insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name="Summary",
        start_index=0,
        end_index=1
    )
    
    print("Result:", result)
    
    # Test 4: Error handling - non-existent sheet
    print("\n📋 Test 4: Error Handling - Non-existent Sheet")
    print("-" * 40)
    
    result = insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name="NonExistentSheet",
        start_index=5,
        end_index=6
    )
    
    print("Result:", result)
    
    # Test 5: Error handling - empty sheet name
    print("\n📋 Test 5: Error Handling - Empty Sheet Name")
    print("-" * 40)
    
    result = insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name="",
        start_index=5,
        end_index=6
    )
    
    print("Result:", result)
    
    # Test 6: Error handling - non-existent spreadsheet
    print("\n📋 Test 6: Error Handling - Non-existent Spreadsheet")
    print("-" * 40)
    
    result = insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name="NonExistentSpreadsheet",
        sheet_name="Sheet1",
        start_index=5,
        end_index=6
    )
    
    print("Result:", result)
    
    # Test 7: Insert large number of rows
    print("\n📋 Test 7: Insert Large Number of Rows")
    print("-" * 40)
    
    result = insert_rows_data(
        drive_service=drive_service,
        sheets_service=sheets_service,
        spreadsheet_name=spreadsheet_name,
        sheet_name="Data",
        start_index=20,
        end_index=30
    )
    
    print("Result:", result)
    
    print("\n" + "=" * 70)
    print("🎯 Insert rows test completed!")

if __name__ == "__main__":
    test_insert_rows() 