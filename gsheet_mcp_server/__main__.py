"""Main entry point for the Google Sheets MCP Server."""

import asyncio
import os
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .server import GoogleSheetsMCPServer


async def main():
    """Run the Google Sheets MCP server."""
    # Get credentials path from environment
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not credentials_path:
        print("Error: GOOGLE_CREDENTIALS_PATH environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    if not Path(credentials_path).exists():
        print(f"Error: Credentials file not found at {credentials_path}", file=sys.stderr)
        sys.exit(1)
    
    # Create and run the server
    server = GoogleSheetsMCPServer(credentials_path)
    
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    asyncio.run(main()) 