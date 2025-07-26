#!/usr/bin/env python3
"""
Test script for the create_data_table_tool functionality.
"""

import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client


async def test_create_data_table():
    """Test the create_data_table_tool."""
    
    # Connect to the MCP server
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            
            # Initialize the session
            await session.initialize()
            
            # Test data for creating a table
            test_headers = ["Name", "Email", "Phone", "Department", "Salary"]
            test_data = [
                ["John Doe", "john.doe@company.com", "555-0101", "Engineering", "$75,000"],
                ["Jane Smith", "jane.smith@company.com", "555-0102", "Marketing", "$65,000"],
                ["Bob Johnson", "bob.johnson@company.com", "555-0103", "Sales", "$70,000"],
                ["Alice Brown", "alice.brown@company.com", "555-0104", "HR", "$60,000"],
                ["Charlie Wilson", "charlie.wilson@company.com", "555-0105", "Engineering", "$80,000"]
            ]
            
            print("🧪 Testing create_data_table_tool...")
            print(f"📊 Creating table with {len(test_headers)} columns and {len(test_data)} rows")
            
            # Call the create_data_table_tool
            result = await session.call_tool("create_data_table_tool", {
                "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",  # Replace with actual ID
                "sheet_name": "Employees",
                "headers": test_headers,
                "data": test_data,
                "table_style": "striped"
            })
            
            print("✅ Table created successfully!")
            print(f"📋 Result: {json.dumps(result.content, indent=2)}")
            
            # Test with different style
            print("\n🧪 Testing with 'default' style...")
            
            result2 = await session.call_tool("create_data_table_tool", {
                "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",  # Replace with actual ID
                "sheet_name": "Products",
                "headers": ["Product", "Category", "Price", "Stock"],
                "data": [
                    ["Laptop", "Electronics", "$999", "50"],
                    ["Mouse", "Electronics", "$25", "200"],
                    ["Desk", "Furniture", "$150", "30"],
                    ["Chair", "Furniture", "$75", "45"]
                ],
                "table_style": "default"
            })
            
            print("✅ Second table created successfully!")
            print(f"📋 Result: {json.dumps(result2.content, indent=2)}")


if __name__ == "__main__":
    print("🚀 Starting create_data_table_tool test...")
    print("⚠️  Make sure to replace 'YOUR_SPREADSHEET_ID_HERE' with an actual spreadsheet ID")
    print("⚠️  Ensure the Google Sheets MCP server is running")
    print()
    
    asyncio.run(test_create_data_table()) 