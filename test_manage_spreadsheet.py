#!/usr/bin/env python3
"""Test script for the new integrated manage_spreadsheet tool."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_manage_spreadsheet():
    """Test the integrated manage_spreadsheet tool."""
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
            
            print("=== Testing Integrated manage_spreadsheet Tool ===\n")
            
            # Test 1: List spreadsheets
            print("1. Testing 'list' action...")
            try:
                result = await session.call_tool("manage_spreadsheet", {
                    "action": "list",
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
            
            # Test 2: Create spreadsheet
            print("2. Testing 'create' action...")
            try:
                result = await session.call_tool("manage_spreadsheet", {
                    "action": "create",
                    "title": "Test Integrated Tool Spreadsheet",
                    "properties": {
                        "sheets": ["Sheet1", "Data", "Summary"]
                    }
                })
                print("Create result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    spreadsheet = result.structuredContent
                    print(f"  Created: {spreadsheet['name']} (ID: {spreadsheet['id']})")
                    print(f"  URL: {spreadsheet['url']}")
                    
                    # Store the ID for next tests
                    test_spreadsheet_id = spreadsheet['id']
                else:
                    test_spreadsheet_id = "test123"  # Fallback
            except Exception as e:
                print(f"Error creating spreadsheet: {e}")
                test_spreadsheet_id = "test123"  # Fallback
            print()
            
            # Test 3: Get spreadsheet info
            print("3. Testing 'get_info' action...")
            try:
                result = await session.call_tool("manage_spreadsheet", {
                    "action": "get_info",
                    "spreadsheet_id": test_spreadsheet_id
                })
                print("Get info result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    metadata = result.structuredContent
                    print(f"  Properties: {metadata.get('properties', {}).get('title', 'Unknown')}")
                    print(f"  Sheets: {len(metadata.get('sheets', []))}")
                    print(f"  Named Ranges: {len(metadata.get('namedRanges', []))}")
                    print(f"  URL: {metadata.get('spreadsheetUrl', 'N/A')}")
            except Exception as e:
                print(f"Error getting spreadsheet info: {e}")
            print()
            
            # Test 4: Update properties
            print("4. Testing 'update_properties' action...")
            try:
                result = await session.call_tool("manage_spreadsheet", {
                    "action": "update_properties",
                    "spreadsheet_id": test_spreadsheet_id,
                    "properties": {
                        "title": "Updated Integrated Tool Spreadsheet"
                    }
                })
                print("Update properties result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    spreadsheet = result.structuredContent
                    print(f"  Updated: {spreadsheet['name']} (ID: {spreadsheet['id']})")
                    print(f"  URL: {spreadsheet['url']}")
            except Exception as e:
                print(f"Error updating properties: {e}")
            print()
            
            print("=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_manage_spreadsheet()) 