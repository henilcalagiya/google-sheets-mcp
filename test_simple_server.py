#!/usr/bin/env python3
"""Test script for the simplified server with two basic tools."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_simple_server():
    """Test the simplified server with two basic tools."""
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
            
            print("=== Testing Simplified Server ===\n")
            
            # Test 1: List spreadsheets
            print("1. Testing list_spreadsheets...")
            try:
                result = await session.call_tool("list_spreadsheets", {
                    "max_results": 3
                })
                print("List result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    spreadsheets = result.structuredContent
                    print(f"Found {len(spreadsheets)} spreadsheets:")
                    for i, spreadsheet in enumerate(spreadsheets):
                        print(f"  {i+1}. {spreadsheet['name']} (ID: {spreadsheet['id']})")
                        print(f"     URL: {spreadsheet['url']}")
            except Exception as e:
                print(f"Error listing spreadsheets: {e}")
            print()
            
            # Test 2: List sheets in a specific spreadsheet
            print("2. Testing list_sheets_in_spreadsheet...")
            try:
                # Use a known spreadsheet ID from the previous test
                test_spreadsheet_id = "16Hni3k_3imVZYnaCcQGnFraQbpLdj5ej7cnXYpRmp3A"
                result = await session.call_tool("list_sheets_in_spreadsheet", {
                    "spreadsheet_id": test_spreadsheet_id
                })
                print("Sheets result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    sheets = result.structuredContent
                    print(f"Found {len(sheets)} sheets:")
                    for i, sheet in enumerate(sheets):
                        print(f"  {i+1}. {sheet['title']} (ID: {sheet['sheet_id']})")
                        print(f"     Rows: {sheet['grid_properties']['rowCount']}, Columns: {sheet['grid_properties']['columnCount']}")
            except Exception as e:
                print(f"Error listing sheets: {e}")
            print()
            
            print("=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_simple_server()) 