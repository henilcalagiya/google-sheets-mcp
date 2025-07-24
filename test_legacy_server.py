#!/usr/bin/env python3
"""Test script for the updated legacy server with integrated manage_spreadsheet tool."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_legacy_server():
    """Test the updated legacy server with integrated manage_spreadsheet tool."""
    # Set up the server parameters
    server_params = StdioServerParameters(
        command="/Users/henil/GSheetMCP Python/venv/bin/python3",
        args=["-m", "gsheet_mcp_server.server"],
        cwd="/Users/henil/GSheetMCP Python",
        env={
            "GOOGLE_CREDENTIALS_PATH": "/Users/henil/GSheetMCP Python/glossy-chimera-466301-c1-a4ae73111b11.json"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("=== Testing Updated Legacy Server ===\n")
            
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
            except Exception as e:
                print(f"Error listing spreadsheets: {e}")
            print()
            
            # Test 2: Create spreadsheet
            print("2. Testing 'create' action...")
            try:
                result = await session.call_tool("manage_spreadsheet", {
                    "action": "create",
                    "title": "Test Legacy Server Spreadsheet",
                    "properties": {
                        "sheets": ["Sheet1", "Data", "Summary"]
                    }
                })
                print("Create result:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {content.text}")
            except Exception as e:
                print(f"Error creating spreadsheet: {e}")
            print()
            
            print("=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_legacy_server()) 