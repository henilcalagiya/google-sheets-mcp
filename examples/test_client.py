"""Test client for the Google Sheets MCP Server."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_gsheet_server():
    """Test the Google Sheets MCP server."""
    # Set up the server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "gsheet_mcp_server.fastmcp_server_simple"],
        env={
            "GOOGLE_CREDENTIALS_PATH": os.getenv("GOOGLE_CREDENTIALS_PATH", "")
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("=== Testing Google Sheets MCP Server ===\n")
            
            # List available tools
            tools_response = await session.list_tools()
            print("Available tools:")
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # Test listing spreadsheets
            print("Testing list_spreadsheets...")
            try:
                result = await session.call_tool("list_spreadsheets", {"max_results": 5})
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
            except Exception as e:
                print(f"Error listing spreadsheets: {e}")
            print()
            
            # Test creating a spreadsheet
            print("Testing create_spreadsheet...")
            try:
                result = await session.call_tool(
                    "create_spreadsheet", 
                    {
                        "title": "Test MCP Spreadsheet",
                        "sheets": ["Sheet1", "Data"]
                    }
                )
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
            except Exception as e:
                print(f"Error creating spreadsheet: {e}")
            print()
            
            # Test searching sheets
            print("Testing search_sheets...")
            try:
                result = await session.call_tool(
                    "search_sheets", 
                    {
                        "query": "test",
                        "max_results": 3
                    }
                )
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
            except Exception as e:
                print(f"Error searching sheets: {e}")


async def main():
    """Main entry point."""
    await test_gsheet_server()


if __name__ == "__main__":
    asyncio.run(main()) 