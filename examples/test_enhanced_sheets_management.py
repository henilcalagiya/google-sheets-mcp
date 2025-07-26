#!/usr/bin/env python3
"""
Test examples for Enhanced Sheets Management Tool.
This demonstrates the combined sheet management and metadata functionality.
"""

import os
import json
from gsheet_mcp_server.handler.sheet_management_handler import sheet_management_handler
from gsheet_mcp_server.fastmcp_server_simple import _setup_google_services

def test_enhanced_sheets_management():
    """Test the enhanced sheets management tool with different metadata options."""
    
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
    
    print(f"\n📊 Testing Enhanced Sheets Management for spreadsheet: {spreadsheet_id}")
    
    try:
        # 1. BASIC OPERATION (No metadata for speed)
        print("\n🔍 1. BASIC OPERATION (No Metadata)")
        print("=" * 50)
        
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=False
        )
        print(f"✅ Basic operation: {result['message']}")
        print(f"📋 Sheets found: {len(result['sheets'])}")
        print(f"⚡ Operations: {result['operations_performed']}")
        
        # 2. ALL SHEETS WITH METADATA
        print("\n🔍 2. ALL SHEETS WITH METADATA")
        print("=" * 50)
        
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=True
        )
        print(f"✅ All sheets with metadata: {result['message']}")
        print(f"📋 Sheets found: {len(result['sheets'])}")
        print(f"📊 Metadata included: {result['operations_performed']['metadata_included']}")
        
        if 'metadata' in result:
            metadata = result['metadata']
            if 'total_sheets' in metadata:
                print(f"📈 Total sheets in metadata: {metadata['total_sheets']}")
            if 'sheets' in metadata:
                print(f"📋 Detailed sheets in metadata: {len(metadata['sheets'])}")
        
        # 3. FOCUS ON SPECIFIC SHEET
        print("\n🔍 3. FOCUS ON SPECIFIC SHEET")
        print("=" * 50)
        
        # Get first sheet name for testing
        if result['sheets']:
            first_sheet_name = result['sheets'][0]['title']
            
            result = sheet_management_handler(
                sheets_service=sheets_service,
                spreadsheet_id=spreadsheet_id,
                include_metadata=True,
                target_sheet_names=[first_sheet_name]
            )
            print(f"✅ Focused on '{first_sheet_name}': {result['message']}")
            print(f"📋 All sheets: {len(result['sheets'])}")
            
            if 'metadata' in result:
                metadata = result['metadata']
                if 'sheet' in metadata:
                    sheet_info = metadata['sheet']
                    print(f"🎯 Focused sheet: {sheet_info['title']}")
                    print(f"   Sheet ID: {sheet_info['sheet_id']}")
                    print(f"   Index: {sheet_info['index']}")
                    print(f"   Hidden: {sheet_info.get('hidden', False)}")
                    print(f"   Grid: {sheet_info.get('grid_properties', {})}")
        
        # 4. ADD SHEETS WITH METADATA
        print("\n🔍 4. ADD SHEETS WITH METADATA")
        print("=" * 50)
        
        # Note: This will actually add sheets to your spreadsheet
        # Uncomment if you want to test this
        """
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            add_sheet_names=["TestSheet1", "TestSheet2"],
            include_metadata=True
        )
        print(f"✅ Added sheets with metadata: {result['message']}")
        print(f"📋 Added sheets: {len(result['added'])}")
        print(f"📊 Operations: {result['operations_performed']}")
        """
        print("⚠️  Add sheets test skipped (would modify spreadsheet)")
        
        # 5. DELETE SHEETS WITH METADATA
        print("\n🔍 5. DELETE SHEETS WITH METADATA")
        print("=" * 50)
        
        # Note: This will actually delete sheets from your spreadsheet
        # Uncomment if you want to test this
        """
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            delete_sheet_ids=[123, 456],  # Replace with actual sheet IDs
            include_metadata=True
        )
        print(f"✅ Deleted sheets with metadata: {result['message']}")
        print(f"🗑️  Deleted sheets: {len(result['deleted'])}")
        print(f"📊 Operations: {result['operations_performed']}")
        """
        print("⚠️  Delete sheets test skipped (would modify spreadsheet)")
        
        # 6. COMPLEX OPERATION
        print("\n🔍 6. COMPLEX OPERATION")
        print("=" * 50)
        
        result = sheet_management_handler(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            include_metadata=True,
            target_sheet_names=["Class Data"]  # Google's sample sheet
        )
        print(f"✅ Complex operation: {result['message']}")
        print(f"📊 Full response structure:")
        print(json.dumps(result, indent=2, default=str))
        
        print("\n🎉 All enhanced sheets management tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_enhanced_sheets_management() 