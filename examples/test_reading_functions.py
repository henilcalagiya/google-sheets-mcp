#!/usr/bin/env python3
"""
Test examples for Google Sheets reading functions.
This demonstrates the three reading options: column-wise, row-wise, and custom range.
"""

import os
import json
from gsheet_mcp_server.handler.read_sheet_data_handler import read_sheet_data, read_multiple_ranges, get_sheet_metadata
from gsheet_mcp_server.fastmcp_server_simple import _setup_google_services

def test_reading_functions():
    """Test the three reading options with a sample spreadsheet."""
    
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
    sheet_name = "Class Data"
    
    print(f"\n📊 Testing reading functions for spreadsheet: {spreadsheet_id}")
    print(f"📋 Sheet: {sheet_name}")
    
    try:
        # 1. COLUMN-WISE READING
        print("\n🔍 1. COLUMN-WISE READING")
        print("=" * 50)
        
        # Read entire column A
        result = read_sheet_data(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            read_type="column",
            range_spec="A"
        )
        print(f"✅ Column A: {result['row_count']} rows, {result['column_count']} columns")
        print(f"📄 First 5 values: {result['values'][:5]}")
        
        # Read column range A1:A10
        result = read_sheet_data(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            read_type="column",
            range_spec="A1:A10"
        )
        print(f"✅ Column A1:A10: {result['row_count']} rows")
        
        # 2. ROW-WISE READING
        print("\n🔍 2. ROW-WISE READING")
        print("=" * 50)
        
        # Read entire row 1
        result = read_sheet_data(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            read_type="row",
            range_spec="1"
        )
        print(f"✅ Row 1: {result['row_count']} rows, {result['column_count']} columns")
        print(f"📄 Values: {result['values']}")
        
        # Read row range 1:5
        result = read_sheet_data(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            read_type="row",
            range_spec="1:5"
        )
        print(f"✅ Rows 1:5: {result['row_count']} rows, {result['column_count']} columns")
        
        # 3. CUSTOM RANGE READING
        print("\n🔍 3. CUSTOM RANGE READING")
        print("=" * 50)
        
        # Read single cell
        result = read_sheet_data(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            read_type="custom",
            range_spec="A1"
        )
        print(f"✅ Single cell A1: {result['values']}")
        
        # Read specific range
        result = read_sheet_data(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            read_type="custom",
            range_spec="A1:B10"
        )
        print(f"✅ Range A1:B10: {result['row_count']} rows, {result['column_count']} columns")
        
        # Read large range
        result = read_sheet_data(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            read_type="custom",
            range_spec="A1:Z100"
        )
        print(f"✅ Large range A1:Z100: {result['row_count']} rows, {result['column_count']} columns")
        
        # 4. MULTIPLE RANGES READING
        print("\n🔍 4. MULTIPLE RANGES READING")
        print("=" * 50)
        
        ranges = [
            f"{sheet_name}!A1:A5",
            f"{sheet_name}!B1:B5", 
            f"{sheet_name}!C1:C5"
        ]
        
        result = read_multiple_ranges(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            ranges=ranges
        )
        print(f"✅ Multiple ranges: {result['total_ranges']} ranges read")
        for i, range_data in enumerate(result['ranges']):
            print(f"   Range {i+1}: {range_data['range']} - {range_data['row_count']} rows")
        
        # 5. SHEET METADATA
        print("\n🔍 5. SHEET METADATA")
        print("=" * 50)
        
        result = get_sheet_metadata(
            sheets_service=sheets_service,
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name
        )
        print(f"✅ Sheet metadata: {json.dumps(result, indent=2)}")
        
        print("\n🎉 All reading tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_reading_functions() 