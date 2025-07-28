#!/usr/bin/env python3
"""
Test example for getting sheet ID from spreadsheet ID and sheet name.
This demonstrates the new utility functions.
"""

import os
from gsheet_mcp_server.helper.spreadsheet_utils import get_sheet_ids_by_names
from gsheet_mcp_server.server import _setup_google_services

def test_sheet_id_lookup():
    """Test getting sheet ID from spreadsheet ID and sheet name."""
    
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
    
    # Sample spreadsheet ID (Google's sample spreadsheet)
    spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    print(f"\n🔍 Testing Sheet ID Lookup for spreadsheet: {spreadsheet_id}")
    print("=" * 70)
    
    # Test 1: Single sheet lookup
    print("\n📋 Test 1: Single Sheet Lookup")
    print("-" * 40)
    
    test_cases = [
        "Class Data",      # Should exist in the sample spreadsheet
        "Sheet1",          # Common sheet name
        "NonExistentSheet" # Should not exist
    ]
    
    try:
        # Use the same function for single sheet lookup
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, test_cases)
        
        for sheet_name in test_cases:
            sheet_id = sheet_ids.get(sheet_name)
            if sheet_id is not None:
                print(f"✅ Found sheet '{sheet_name}' with ID: {sheet_id}")
            else:
                print(f"❌ Sheet '{sheet_name}' not found")
                
    except Exception as e:
        print(f"❌ Error in single sheet lookup: {e}")
    
    # Test 2: Multiple sheet lookup
    print("\n📋 Test 2: Multiple Sheet Lookup")
    print("-" * 40)
    
    sheet_names = ["Class Data", "Sheet1", "NonExistentSheet", "AnotherSheet"]
    
    try:
        sheet_ids = get_sheet_ids_by_names(sheets_service, spreadsheet_id, sheet_names)
        
        print("Results:")
        for sheet_name, sheet_id in sheet_ids.items():
            if sheet_id is not None:
                print(f"  ✅ '{sheet_name}' → ID: {sheet_id}")
            else:
                print(f"  ❌ '{sheet_name}' → Not found")
                
    except Exception as e:
        print(f"❌ Error in multiple sheet lookup: {e}")
    
    # Test 3: Practical usage example
    print("\n📋 Test 3: Practical Usage Example")
    print("-" * 40)
    
    # Simulate a scenario where you want to delete sheets by name
    sheets_to_delete = ["Sheet1", "Class Data"]
    
    print(f"Want to delete sheets: {sheets_to_delete}")
    
    try:
        # Get sheet IDs for the sheets we want to delete
        sheet_id_map = get_sheet_ids_by_names(sheets_service, spreadsheet_id, sheets_to_delete)
        
        # Filter out sheets that don't exist
        existing_sheet_ids = []
        for sheet_name, sheet_id in sheet_id_map.items():
            if sheet_id is not None:
                existing_sheet_ids.append(sheet_id)
                print(f"  ✅ Will delete '{sheet_name}' (ID: {sheet_id})")
            else:
                print(f"  ⚠️  Cannot delete '{sheet_name}' (not found)")
        
        if existing_sheet_ids:
            print(f"\n📊 Summary: {len(existing_sheet_ids)} sheets ready for deletion")
            print(f"Sheet IDs: {existing_sheet_ids}")
        else:
            print("\n📊 Summary: No sheets found for deletion")
            
    except Exception as e:
        print(f"❌ Error in practical example: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 Sheet ID lookup test completed!")

if __name__ == "__main__":
    test_sheet_id_lookup() 