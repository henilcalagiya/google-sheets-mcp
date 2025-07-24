#!/usr/bin/env python3
"""Test script for the new add_sheets_to_spreadsheet tool."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_add_sheets():
    """Test the add_sheets_to_spreadsheet tool."""
    # Set up the server parameters
    server_params = StdioServerParameters(
        command="/Users/henil/GSheetMCP Python/venv/bin/python3",
        args=["-m", "gsheet_mcp_server.fastmcp_server_simple"],
        cwd="/Users/henil/GSheetMCP Python",
        env={
            "GOOGLE_CREDENTIALS_PATH": "/Users/henil/GSheetMCP Python/glossy-chimera-466301-c1-a4ae73111b11.json"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("=== Testing add_sheets_to_spreadsheet Tool ===\n")
            
            # Test spreadsheet ID
            test_spreadsheet_id = "16Hni3k_3imVZYnaCcQGnFraQbpLdj5ej7cnXYpRmp3A"
            
            # Test 1: List current sheets
            print("1. Current sheets in spreadsheet:")
            try:
                result = await session.call_tool("list_sheets_in_spreadsheet", {
                    "spreadsheet_id": test_spreadsheet_id
                })
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
            except Exception as e:
                print(f"Error listing sheets: {e}")
            print()
            
            # Test 2: Add new sheets
            print("2. Adding new sheets...")
            try:
                result = await session.call_tool("add_sheets_to_spreadsheet", {
                    "spreadsheet_id": test_spreadsheet_id,
                    "sheet_names": ["Test Sheet 1", "Test Sheet 2", "Data Analysis"]
                })
                print("Add sheets result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    sheets = result.structuredContent
                    print(f"Added {len(sheets)} new sheets:")
                    for i, sheet in enumerate(sheets):
                        print(f"  {i+1}. {sheet['title']} (ID: {sheet['sheet_id']})")
                        print(f"     Rows: {sheet['grid_properties']['rowCount']}, Columns: {sheet['grid_properties']['columnCount']}")
            except Exception as e:
                print(f"Error adding sheets: {e}")
            print()
            
            # Test 3: List sheets again to confirm
            print("3. Updated sheets in spreadsheet:")
            try:
                result = await session.call_tool("list_sheets_in_spreadsheet", {
                    "spreadsheet_id": test_spreadsheet_id
                })
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
            except Exception as e:
                print(f"Error listing sheets: {e}")
            print()
            
            print("=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_add_sheets()) 