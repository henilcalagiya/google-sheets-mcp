"""Main entry point for the Google Sheets MCP Server."""

import os
import sys
from pathlib import Path

from .server import mcp


def main():
    """Run the Google Sheets MCP server."""
    # Get credentials path from environment
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not credentials_path:
        print("Error: GOOGLE_CREDENTIALS_PATH environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    if not Path(credentials_path).exists():
        print(f"Error: Credentials file not found at {credentials_path}", file=sys.stderr)
        sys.exit(1)
    
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main() 