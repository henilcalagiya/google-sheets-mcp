"""Main entry point for the Google Sheets MCP Server."""

import os
import sys
from pathlib import Path

from .server import mcp


def main():
    """Run the Google Sheets MCP server."""
    # The server now uses environment variables only
    # The server.py file handles all the credential validation
    # Just run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main() 