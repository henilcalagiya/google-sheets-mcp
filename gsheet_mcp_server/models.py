from typing import Any, Dict
from pydantic import BaseModel, Field

class SpreadsheetInfo(BaseModel):
    """Spreadsheet information structure."""
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    name: str = Field(description="Spreadsheet name")

class SheetInfo(BaseModel):
    """Sheet information structure."""
    sheet_id: int = Field(description="Sheet ID")
    title: str = Field(description="Sheet title")
    index: int = Field(description="Sheet index")
    grid_properties: Dict[str, Any] = Field(description="Grid properties (rows, columns)") 