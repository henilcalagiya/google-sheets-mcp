#!/usr/bin/env python3
"""
Simple example showing how to use get_sheet_ids_by_names for both single and multiple lookups.
"""

import os
from gsheet_mcp_server.helper.spreadsheet_utils import get_sheet_ids_by_names
from gsheet_mcp_server.server import _setup_google_services

def simple_example():
    """Demonstrate single and multiple sheet ID lookups."""
    
    # Setup (you would normally get these from environment)
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
    
    # Sample spreadsheet ID
    spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    print("\n🎯 Sheet ID Lookup Examples")
    print("=" * 50)
    
    # Example 1: Single sheet lookup
    print("\n📋 Example 1: Single Sheet")
    sheet_name = "Class Data"
    result = get_sheet_ids_by_names(sheets_service, spreadsheet_id, [sheet_name])
    
    if result[sheet_name]:
        print(f"✅ Found '{sheet_name}' with ID: {result[sheet_name]}")
    else:
        print(f"❌ '{sheet_name}' not found")
    
    # Example 2: Multiple sheet lookup
    print("\n📋 Example 2: Multiple Sheets")
    sheet_names = ["Class Data", "Sheet1", "NonExistentSheet"]
    result = get_sheet_ids_by_names(sheets_service, spreadsheet_id, sheet_names)
    
    for name, sheet_id in result.items():
        if sheet_id is not None:
            print(f"✅ '{name}' → ID: {sheet_id}")
        else:
            print(f"❌ '{name}' → Not found")
    
    # Example 3: Practical usage - get IDs for deletion
    print("\n📋 Example 3: Practical Usage")
    sheets_to_delete = ["Sheet1", "Class Data"]
    sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, sheets_to_delete)
    
    # Extract only existing sheet IDs
    existing_ids = [id for id in sheet_ids.values() if id is not None]
    
    if existing_ids:
        print(f"📊 Ready to delete {len(existing_ids)} sheets with IDs: {existing_ids}")
    else:
        print("📊 No sheets found for deletion")
    
    print("\n" + "=" * 50)
    print("✅ Examples completed!")

if __name__ == "__main__":
    simple_example() 