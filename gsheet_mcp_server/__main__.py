#!/usr/bin/env python3
"""
Google Sheets MCP Server - Direct Execution Entry Point
This allows one-line execution: uvx google-sheets-mcp@latest
Environment variables are provided by the MCP client configuration.
"""

import os
import sys

def main():
    """Main entry point for direct execution."""
    print("🚀 Google Sheets MCP Server")
    print("📦 Package: google-sheets-mcp")
    print("🛠️ Powerful tools for Google Sheets automation")
    print("💡 Environment Variables from MCP Config")
    print("=" * 50)
    
    print("\n✅ Starting MCP server...")
    print("🔌 Ready to connect with MCP clients!")
    print("📋 Available tools: Google Sheets operations")
    print("💡 Environment variables provided by MCP client configuration")
    print("=" * 50)
    
    # Import and run the MCP server
    try:
        from gsheet_mcp_server.server import mcp
        mcp.run()
    except ImportError as e:
        print("❌ Error: Could not import MCP server")
        print(f"💡 Error details: {e}")
        print("💡 This package is designed to be used with MCP clients")
        print("💡 Configure your MCP client to use this package")
        sys.exit(1)

if __name__ == "__main__":
    main()
