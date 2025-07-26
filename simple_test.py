#!/usr/bin/env python3
"""Simple test for the manage_spreadsheet tool."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def simple_test():
    """Simple test of the manage_spreadsheet tool."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "gsheet_mcp_server.server"],
        cwd="/Users/henil/GSheetMCP Python",
        env={
            "GOOGLE_CREDENTIALS_PATH": "/Users/henil/GSheetMCP Python/glossy-chimera-466301-c1-a4ae73111b11.json"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("=== Simple Test of manage_spreadsheet Tool ===\n")
            
            # Test list action
            print("Testing 'list' action...")
            try:
                result = await session.call_tool("manage_spreadsheet", {
                    "action": "list",
                    "max_results": 2
                })
                print("✅ List action completed successfully")
                print(f"Result type: {type(result)}")
                print(f"Content count: {len(result.content)}")
                for i, content in enumerate(result.content):
                    print(f"Content {i}: {type(content)}")
                    if hasattr(content, 'text'):
                        print(f"  Text: {content.text[:100]}...")
            except Exception as e:
                print(f"❌ Error in list action: {e}")
            
            print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(simple_test()) 