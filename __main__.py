#!/usr/bin/env python3
"""
Google Sheets MCP Server - Direct Execution Entry Point
This allows one-line execution: uvx google-sheets-mcp@latest
Environment variables are provided by the MCP client configuration.
"""

import os
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gsheet_mcp_server.server import mcp

def main():
    """Main entry point for direct execution."""
    print("🚀 Google Sheets MCP Server")
    print("📦 Package: google-sheets-mcp")
    print("🛠️ 25 powerful tools for Google Sheets automation")
    print("💡 Environment Variables from MCP Config")
    print("=" * 50)
    
    print("\n✅ Starting MCP server...")
    print("🔌 Ready to connect with MCP clients!")
    print("📋 Available tools: 25 Google Sheets operations")
    print("💡 Environment variables provided by MCP client configuration")
    print("=" * 50)
    
    # Run the MCP server
    mcp.run()

if __name__ == "__main__":
    main()
