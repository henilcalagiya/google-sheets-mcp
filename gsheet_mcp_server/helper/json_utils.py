"""
JSON utilities for compact serialization to reduce newlines and character count.
"""

import json
from typing import Any, Dict


def compact_json_response(data: Dict[str, Any]) -> str:
    """
    Convert a Python dictionary to a compact JSON string with no newlines or extra spaces.
    
    Args:
        data: Python dictionary to serialize
    
    Returns:
        Compact JSON string with minimal formatting
    """
    return json.dumps(data, separators=(',', ':'))


def compact_json_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert nested dictionaries to compact JSON strings to reduce newlines.
    This is useful for large nested objects that cause many newlines.
    
    Args:
        data: Python dictionary with potentially large nested objects
    
    Returns:
        Dictionary with large nested objects converted to compact JSON strings
    """
    result = {}
    
    for key, value in data.items():
        if isinstance(value, dict) and len(str(value)) > 100:
            # Convert large nested objects to compact JSON strings
            result[key] = compact_json_response(value)
        elif isinstance(value, list) and len(str(value)) > 100:
            # Convert large lists to compact JSON strings
            result[key] = compact_json_response(value)
        else:
            result[key] = value
    
    return result


def create_compact_response(success: bool, message: str, data: Dict[str, Any] = None) -> str:
    """
    Create a compact JSON response string.
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Optional data dictionary
    
    Returns:
        Compact JSON response string
    """
    response = {
        "success": success,
        "message": message
    }
    
    if data:
        response["data"] = data
    
    return compact_json_response(response) 