#!/usr/bin/env python3
"""Test script for the new list_sheets_in_spreadsheet tool."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_list_sheets():
    """Test the list_sheets_in_spreadsheet tool."""
    # Set up the server parameters
    server_params = StdioServerParameters(
        command="/Users/henil/GSheetMCP Python/venv/bin/python3",
        args=["-m", "gsheet_mcp_server.fastmcp_server"],
        cwd="/Users/henil/GSheetMCP Python",
        env={
            "GOOGLE_CREDENTIALS_PATH": "/Users/henil/GSheetMCP Python/glossy-chimera-466301-c1-a4ae73111b11.json"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("=== Testing list_sheets_in_spreadsheet Tool ===\n")
            
            # First, get a list of spreadsheets to test with
            print("1. Getting list of available spreadsheets...")
            try:
                result = await session.call_tool("list_spreadsheets", {"max_results": 3})
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    spreadsheets = result.structuredContent
                    print(f"Found {len(spreadsheets)} spreadsheets:")
                    for i, spreadsheet in enumerate(spreadsheets):
                        print(f"  {i+1}. {spreadsheet['name']} (ID: {spreadsheet['id']})")
                    
                    if spreadsheets:
                        # Test with the first spreadsheet
                        test_spreadsheet_id = spreadsheets[0]['id']
                        print(f"\n2. Testing list_sheets_in_spreadsheet with: {test_spreadsheet_id}")
                        
                        try:
                            sheets_result = await session.call_tool(
                                "list_sheets_in_spreadsheet", 
                                {"spreadsheet_id": test_spreadsheet_id}
                            )
                            
                            print("Sheets found:")
                            if hasattr(sheets_result, 'structuredContent') and sheets_result.structuredContent:
                                for sheet in sheets_result.structuredContent:
                                    print(f"  - {sheet['title']} (ID: {sheet['sheet_id']})")
                                    print(f"    Grid: {sheet['grid_properties']['rowCount']} rows x {sheet['grid_properties']['columnCount']} columns")
                                    print(f"    Index: {sheet['index']}")
                            else:
                                for content in sheets_result.content:
                                    if hasattr(content, 'text'):
                                        print(f"  {content.text}")
                        except Exception as e:
                            print(f"Error listing sheets: {e}")
                    else:
                        print("No spreadsheets found to test with.")
                else:
                    print("No structured content returned from list_spreadsheets")
            except Exception as e:
                print(f"Error listing spreadsheets: {e}")
            
            print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_list_sheets()) 