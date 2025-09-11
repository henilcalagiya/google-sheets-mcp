"""Basic tests for Google Sheets MCP Server."""

import pytest


def test_version():
    """Test that version is properly defined."""
    from gsheet_mcp_server import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_import():
    """Test that the main module can be imported."""
    import gsheet_mcp_server
    assert gsheet_mcp_server is not None


def test_placeholder():
    """Placeholder test to ensure pytest runs successfully."""
    assert True
