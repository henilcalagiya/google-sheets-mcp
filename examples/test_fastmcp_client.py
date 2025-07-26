"""Test client for the Google Sheets FastMCP Server."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.shared.metadata_utils import get_display_name


async def test_fastmcp_server():
    """Test the Google Sheets FastMCP server."""
    # Set up the server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "gsheet_mcp_server.server"],
        env={
            "GOOGLE_CREDENTIALS_PATH": os.getenv("GOOGLE_CREDENTIALS_PATH", "")
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("=== Testing Google Sheets FastMCP Server ===\n")
            
            # List available tools
            tools_response = await session.list_tools()
            print("Available tools:")
            for tool in tools_response.tools:
                display_name = get_display_name(tool)
                print(f"  - {display_name}: {tool.description}")
            print()
            
            # List available resources
            resources_response = await session.list_resources()
            print("Available resources:")
            for resource in resources_response.resources:
                display_name = get_display_name(resource)
                print(f"  - {display_name} ({resource.uri})")
            print()
            
            # List available prompts
            prompts_response = await session.list_prompts()
            print("Available prompts:")
            for prompt in prompts_response.prompts:
                display_name = get_display_name(prompt)
                print(f"  - {display_name}: {prompt.description}")
            print()
            
            # Test structured output tools
            print("Testing structured output tools...")
            
            # Test list_spreadsheets (returns structured data)
            try:
                result = await session.call_tool("list_spreadsheets", {"max_results": 3})
                print("list_spreadsheets result:")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    for spreadsheet in result.structuredContent:
                        print(f"  - {spreadsheet['name']} (ID: {spreadsheet['id']})")
                else:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(f"  {content.text}")
            except Exception as e:
                print(f"Error listing spreadsheets: {e}")
            print()
            

            
            # Test resources
            print("Testing resources...")
            
            # Test greeting resource
            try:
                resource_content = await session.read_resource("greeting://World")
                content_block = resource_content.contents[0]
                if isinstance(content_block, types.TextContent):
                    print(f"Greeting resource: {content_block.text}")
            except Exception as e:
                print(f"Error reading greeting resource: {e}")
            
            # Test spreadsheet resource (if we have a spreadsheet ID)
            try:
                # This would need a real spreadsheet ID
                # resource_content = await session.read_resource("spreadsheet://1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
                # content_block = resource_content.contents[0]
                # if isinstance(content_block, types.TextContent):
                #     print(f"Spreadsheet resource: {content_block.text}")
                print("Spreadsheet resource test skipped (needs real spreadsheet ID)")
            except Exception as e:
                print(f"Error reading spreadsheet resource: {e}")
            print()
            
            # Test prompts
            print("Testing prompts...")
            
            # Test analyze_spreadsheet prompt
            try:
                if prompts_response.prompts:
                    prompt_name = "analyze_spreadsheet"
                    prompt = await session.get_prompt(
                        prompt_name, 
                        arguments={"spreadsheet_id": "test123", "analysis_type": "summary"}
                    )
                    print(f"analyze_spreadsheet prompt:")
                    for message in prompt.messages:
                        if hasattr(message, 'content'):
                            for content in message.content:
                                if hasattr(content, 'text'):
                                    print(f"  {content.text}")
            except Exception as e:
                print(f"Error getting prompt: {e}")
            print()
            
            # Test text-based tools
            print("Testing text-based tools...")
            
            # Test read_sheet (returns text)
            try:
                # This would need a real spreadsheet ID
                # result = await session.call_tool("read_sheet", {"spreadsheet_id": "test123"})
                # for content in result.content:
                #     if hasattr(content, 'text'):
                #         print(f"read_sheet result: {content.text}")
                print("read_sheet test skipped (needs real spreadsheet ID)")
            except Exception as e:
                print(f"Error reading sheet: {e}")
            
            # Test create_spreadsheet
            try:
                result = await session.call_tool(
                    "create_spreadsheet", 
                    {
                        "title": "Test MCP Spreadsheet",
                        "sheets": ["Sheet1", "Data"]
                    }
                )
                print("create_spreadsheet result:")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    spreadsheet = result.structuredContent
                    print(f"  Created: {spreadsheet['name']} (ID: {spreadsheet['id']})")
                    print(f"  URL: {spreadsheet['url']}")
                else:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(f"  {content.text}")
            except Exception as e:
                print(f"Error creating spreadsheet: {e}")
            print()
            
            # Test search_sheets
            try:
                result = await session.call_tool(
                    "search_sheets", 
                    {
                        "query": "test",
                        "max_results": 3
                    }
                )
                print("search_sheets result:")
                if hasattr(result, 'structuredContent') and result.structuredContent:
                    for result_item in result.structuredContent:
                        print(f"  - {result_item['spreadsheet']} - {result_item['sheet']} {result_item['cell']}")
                        print(f"    Value: {result_item['value']}")
                else:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(f"  {content.text}")
            except Exception as e:
                print(f"Error searching sheets: {e}")
            print()
            
            # Test list_sheets_in_spreadsheet
            try:
                # This would need a real spreadsheet ID
                # result = await session.call_tool("list_sheets_in_spreadsheet", {"spreadsheet_id": "test123"})
                # print("list_sheets_in_spreadsheet result:")
                # if hasattr(result, 'structuredContent') and result.structuredContent:
                #     for sheet in result.structuredContent:
                #         print(f"  - {sheet['title']} (ID: {sheet['sheet_id']})")
                #         print(f"    Grid: {sheet['grid_properties']['rowCount']} rows x {sheet['grid_properties']['columnCount']} columns")
                # else:
                #     for content in result.content:
                #         if hasattr(content, 'text'):
                #             print(f"  {content.text}")
                print("list_sheets_in_spreadsheet test skipped (needs real spreadsheet ID)")
            except Exception as e:
                print(f"Error listing sheets: {e}")
            print()
            
            print("=== Test Complete ===")


async def main():
    """Main entry point."""
    await test_fastmcp_server()


if __name__ == "__main__":
    asyncio.run(main()) 