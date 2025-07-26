#!/usr/bin/env python3
"""
Test examples for Enhanced Sheets Management Tool with Multiple Sheets Metadata.
This demonstrates the new functionality to get metadata for multiple specific sheets.
"""

import os
import json
from gsheet_mcp_server.handler.sheet_management_handler import sheet_management_handler
from gsheet_mcp_server.server import _setup_google_services

def test_multiple_sheets_metadata():
    """Test the enhanced sheets management tool with multiple target sheets."""
    
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
    
    # Sample spreadsheet ID (replace with your actual spreadsheet ID)
    spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"  # Google's sample spreadsheet
    
    print(f"\n📊 Testing Multiple Sheets Metadata for spreadsheet: {spreadsheet_id}")
    
    try:
        # 1. GET ALL SHEETS FIRST (to see available sheet names)
        print("\n🔍 1. GET ALL SHEETS (to see available names)")
        print("=" * 50)
        
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=False
        )
        
        available_sheets = [sheet['title'] for sheet in result['sheets']]
        print(f"✅ Available sheets: {available_sheets}")
        
        if len(available_sheets) < 2:
            print("⚠️  Need at least 2 sheets to test multiple sheets functionality")
            return
        
        # 2. SINGLE SHEET FOCUS
        print("\n🔍 2. SINGLE SHEET FOCUS")
        print("=" * 50)
        
        single_sheet = available_sheets[0]
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=True,
            target_sheet_names=[single_sheet]
        )
        
        print(f"✅ Single sheet focus on '{single_sheet}': {result['message']}")
        if 'metadata' in result and 'focused_sheets' in result['metadata']:
            focused_sheets = result['metadata']['focused_sheets']
            print(f"📋 Focused sheets: {len(focused_sheets)}")
            for sheet in focused_sheets:
                if 'error' not in sheet:
                    print(f"   📄 {sheet['title']}: ID={sheet['sheet_id']}, Index={sheet['index']}")
                else:
                    print(f"   ❌ {sheet['sheet_name']}: {sheet['error']}")
        
        # 3. MULTIPLE SHEETS FOCUS
        print("\n🔍 3. MULTIPLE SHEETS FOCUS")
        print("=" * 50)
        
        # Take first 2 sheets for testing
        multiple_sheets = available_sheets[:2]
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=True,
            target_sheet_names=multiple_sheets
        )
        
        print(f"✅ Multiple sheets focus on {multiple_sheets}: {result['message']}")
        if 'metadata' in result and 'focused_sheets' in result['metadata']:
            focused_sheets = result['metadata']['focused_sheets']
            print(f"📋 Focused sheets: {len(focused_sheets)}")
            for sheet in focused_sheets:
                if 'error' not in sheet:
                    print(f"   📄 {sheet['title']}: ID={sheet['sheet_id']}, Index={sheet['index']}")
                    print(f"      Grid: {sheet.get('grid_properties', {})}")
                    print(f"      Hidden: {sheet.get('hidden', False)}")
                else:
                    print(f"   ❌ {sheet['sheet_name']}: {sheet['error']}")
        
        # 4. ALL SHEETS METADATA (for comparison)
        print("\n🔍 4. ALL SHEETS METADATA (for comparison)")
        print("=" * 50)
        
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=True,
            target_sheet_names=[]  # Empty list = all sheets
        )
        
        print(f"✅ All sheets metadata: {result['message']}")
        if 'metadata' in result:
            if 'total_sheets' in result['metadata']:
                print(f"📈 Total sheets: {result['metadata']['total_sheets']}")
            if 'sheets' in result['metadata']:
                print(f"📋 Detailed sheets: {len(result['metadata']['sheets'])}")
        
        # 5. MIXED OPERATION (Add sheets + Multiple metadata)
        print("\n🔍 5. MIXED OPERATION (Add sheets + Multiple metadata)")
        print("=" * 50)
        
        # Note: This will actually add sheets to your spreadsheet
        # Uncomment if you want to test this
        """
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            add_sheet_names=["TestSheet1", "TestSheet2"],
            include_metadata=True,
            target_sheet_names=["TestSheet1", "TestSheet2"]
        )
        
        print(f"✅ Mixed operation: {result['message']}")
        print(f"📋 Added sheets: {len(result['added'])}")
        print(f"📊 Operations: {result['operations_performed']}")
        
        if 'metadata' in result and 'focused_sheets' in result['metadata']:
            focused_sheets = result['metadata']['focused_sheets']
            print(f"📋 Focused metadata for {len(focused_sheets)} sheets")
        """
        print("⚠️  Mixed operation test skipped (would modify spreadsheet)")
        
        # 6. ERROR HANDLING (Non-existent sheets)
        print("\n🔍 6. ERROR HANDLING (Non-existent sheets)")
        print("=" * 50)
        
        non_existent_sheets = ["NonExistentSheet1", "NonExistentSheet2"]
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=True,
            target_sheet_names=non_existent_sheets
        )
        
        print(f"✅ Error handling test: {result['message']}")
        if 'metadata' in result and 'focused_sheets' in result['metadata']:
            focused_sheets = result['metadata']['focused_sheets']
            print(f"📋 Results for {len(focused_sheets)} requested sheets:")
            for sheet in focused_sheets:
                if 'error' in sheet:
                    print(f"   ❌ {sheet['sheet_name']}: {sheet['error']}")
                else:
                    print(f"   ✅ {sheet['title']}: Found successfully")
        
        # 7. COMPLEX OPERATION (Multiple sheets + Operations)
        print("\n🔍 7. COMPLEX OPERATION (Multiple sheets + Operations)")
        print("=" * 50)
        
        # Use existing sheets for testing
        test_sheets = available_sheets[:min(3, len(available_sheets))]
        
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=True,
            target_sheet_names=test_sheets
        )
        
        print(f"✅ Complex operation: {result['message']}")
        print(f"📊 Full response structure:")
        print(json.dumps(result, indent=2, default=str))
        
        print("\n🎉 All multiple sheets metadata tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_multiple_sheets_metadata() 