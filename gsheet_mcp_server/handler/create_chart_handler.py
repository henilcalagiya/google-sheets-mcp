from typing import Dict, Any, List, Optional
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name
from gsheet_mcp_server.helper.json_utils import compact_json_response


class CreateChartRequest(BaseModel):
    """Request model for creating charts."""
    spreadsheet_name: str = Field(..., description="The name of the spreadsheet")
    sheet_name: str = Field(..., description="Name of the sheet to create chart in")
    chart_type: str = Field(..., description="Type of chart: BAR, COLUMN, LINE, PIE, SCATTER, AREA, COMBO")
    data_range: str = Field(..., description="Data range for chart (e.g., 'A1:B10')")
    title: str = Field(default="", description="Chart title")
    position: Dict[str, Any] = Field(default_factory=dict, description="Chart position and size")
    series_names: Optional[List[str]] = Field(default=None, description="Names for data series")


class CreateChartResponse(BaseModel):
    """Response model for creating charts."""
    spreadsheet_name: str
    sheet_name: str
    chart_id: int
    chart_type: str
    data_range: str
    title: str
    message: str


def create_chart(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    chart_type: str,
    data_range: str,
    title: str = "",
    position: Dict[str, Any] = None,
    series_names: List[str] = None
) -> str:
    """
    Create a chart in Google Sheets with specified type and configuration.
    
    Supported chart types:
    - BAR: Horizontal bar chart
    - COLUMN: Vertical column chart  
    - LINE: Line chart
    - PIE: Pie chart
    - SCATTER: Scatter plot
    - AREA: Area chart
    - COMBO: Combination chart
    
    Args:
        drive_service: Google Drive API service
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to create chart in
        chart_type: Type of chart to create
        data_range: Range containing chart data (e.g., 'A1:B10')
        title: Chart title
        position: Chart position and size (optional)
        series_names: Names for data series (optional)
    
    Returns:
        Compact JSON string containing chart creation results
        
    Raises:
        RuntimeError: If chart creation fails
    """
    try:
        # Get spreadsheet ID
        spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
        
        # Validate chart type
        valid_chart_types = ['BAR', 'COLUMN', 'LINE', 'PIE', 'SCATTER', 'AREA', 'COMBO']
        if chart_type.upper() not in valid_chart_types:
            return compact_json_response({
                "success": False,
                "message": f"Invalid chart type. Must be one of: {valid_chart_types}"
            })
        
        # Default position if not provided
        if position is None:
            position = {
                "overlayPosition": {
                    "anchorCell": {
                        "sheetId": 0,
                        "rowIndex": 0,
                        "columnIndex": 0
                    },
                    "widthPixels": 400,
                    "heightPixels": 300
                }
            }
        
        # Create chart specification
        chart_spec = _create_chart_specification(
            chart_type, data_range, title, series_names
        )
        
        # Create the chart
        request_body = {
            "requests": [
                {
                    "addChart": {
                        "chart": {
                            "spec": chart_spec,
                            "position": position
                        }
                    }
                }
            ]
        }
        
        # Execute the request
        response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        # Extract chart ID from response
        chart_id = None
        if 'replies' in response and response['replies']:
            chart_id = response['replies'][0].get('addChart', {}).get('chart', {}).get('chartId')
        
        return compact_json_response({
            "success": True,
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "chart_id": chart_id,
            "chart_type": chart_type.upper(),
            "data_range": data_range,
            "title": title,
            "position": position,
            "message": f"Successfully created {chart_type.lower()} chart with title '{title}' using data range '{data_range}'"
        })
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        return compact_json_response({
            "success": False,
            "message": f"Error creating chart: {error_message}"
        })
    except Exception as error:
        return compact_json_response({
            "success": False,
            "message": f"Unexpected error creating chart: {error}"
        })


def _create_chart_specification(
    chart_type: str,
    data_range: str,
    title: str,
    series_names: List[str] = None
) -> Dict[str, Any]:
    """Create chart specification based on chart type."""
    
    # Base chart spec
    chart_spec = {
        "title": {
            "textFormat": {
                "bold": True,
                "fontSize": 14
            }
        }
    }
    
    if title:
        chart_spec["title"]["text"] = title
    
    # Add chart type specific configuration
    if chart_type.upper() == 'BAR':
        chart_spec["basicChart"] = {
            "chartType": "BAR",
            "legendPosition": "BOTTOM_LEGEND",
            "axis": [
                {
                    "position": "BOTTOM_AXIS",
                    "title": "Categories"
                },
                {
                    "position": "LEFT_AXIS", 
                    "title": "Values"
                }
            ],
            "domains": [
                {
                    "domain": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 1
                                }
                            ]
                        }
                    }
                }
            ],
            "series": [
                {
                    "series": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 1,
                                    "endColumnIndex": 2
                                }
                            ]
                        }
                    },
                    "targetAxis": "LEFT_AXIS"
                }
            ]
        }
    
    elif chart_type.upper() == 'COLUMN':
        chart_spec["basicChart"] = {
            "chartType": "COLUMN",
            "legendPosition": "BOTTOM_LEGEND",
            "axis": [
                {
                    "position": "BOTTOM_AXIS",
                    "title": "Categories"
                },
                {
                    "position": "LEFT_AXIS",
                    "title": "Values"
                }
            ],
            "domains": [
                {
                    "domain": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 1
                                }
                            ]
                        }
                    }
                }
            ],
            "series": [
                {
                    "series": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 1,
                                    "endColumnIndex": 2
                                }
                            ]
                        }
                    },
                    "targetAxis": "LEFT_AXIS"
                }
            ]
        }
    
    elif chart_type.upper() == 'LINE':
        chart_spec["basicChart"] = {
            "chartType": "LINE",
            "legendPosition": "BOTTOM_LEGEND",
            "axis": [
                {
                    "position": "BOTTOM_AXIS",
                    "title": "Categories"
                },
                {
                    "position": "LEFT_AXIS",
                    "title": "Values"
                }
            ],
            "domains": [
                {
                    "domain": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 1
                                }
                            ]
                        }
                    }
                }
            ],
            "series": [
                {
                    "series": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 1,
                                    "endColumnIndex": 2
                                }
                            ]
                        }
                    },
                    "targetAxis": "LEFT_AXIS"
                }
            ]
        }
    
    elif chart_type.upper() == 'PIE':
        chart_spec["pieChart"] = {
            "legendPosition": "BOTTOM_LEGEND",
            "domain": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1
                        }
                    ]
                }
            },
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2
                        }
                    ]
                }
            }
        }
    
    elif chart_type.upper() == 'SCATTER':
        chart_spec["basicChart"] = {
            "chartType": "SCATTER",
            "legendPosition": "BOTTOM_LEGEND",
            "axis": [
                {
                    "position": "BOTTOM_AXIS",
                    "title": "X Values"
                },
                {
                    "position": "LEFT_AXIS",
                    "title": "Y Values"
                }
            ],
            "domains": [
                {
                    "domain": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 1
                                }
                            ]
                        }
                    }
                }
            ],
            "series": [
                {
                    "series": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 1,
                                    "endColumnIndex": 2
                                }
                            ]
                        }
                    },
                    "targetAxis": "LEFT_AXIS"
                }
            ]
        }
    
    elif chart_type.upper() == 'AREA':
        chart_spec["basicChart"] = {
            "chartType": "AREA",
            "legendPosition": "BOTTOM_LEGEND",
            "axis": [
                {
                    "position": "BOTTOM_AXIS",
                    "title": "Categories"
                },
                {
                    "position": "LEFT_AXIS",
                    "title": "Values"
                }
            ],
            "domains": [
                {
                    "domain": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 1
                                }
                            ]
                        }
                    }
                }
            ],
            "series": [
                {
                    "series": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 1,
                                    "endColumnIndex": 2
                                }
                            ]
                        }
                    },
                    "targetAxis": "LEFT_AXIS"
                }
            ]
        }
    
    elif chart_type.upper() == 'COMBO':
        chart_spec["basicChart"] = {
            "chartType": "COMBO",
            "legendPosition": "BOTTOM_LEGEND",
            "axis": [
                {
                    "position": "BOTTOM_AXIS",
                    "title": "Categories"
                },
                {
                    "position": "LEFT_AXIS",
                    "title": "Values"
                }
            ],
            "domains": [
                {
                    "domain": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 1
                                }
                            ]
                        }
                    }
                }
            ],
            "series": [
                {
                    "series": {
                        "sourceRange": {
                            "sources": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 0,
                                    "endRowIndex": 1,
                                    "startColumnIndex": 1,
                                    "endColumnIndex": 2
                                }
                            ]
                        }
                    },
                    "targetAxis": "LEFT_AXIS"
                }
            ]
        }
    
    return chart_spec 