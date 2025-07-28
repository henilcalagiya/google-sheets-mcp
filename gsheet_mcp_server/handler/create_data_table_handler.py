from typing import List, Dict, Any
from googleapiclient.errors import HttpError
from gsheet_mcp_server.helper.spreadsheet_utils import get_spreadsheet_id_by_name


def create_data_table(
    drive_service,
    sheets_service,
    spreadsheet_name: str,
    sheet_name: str,
    headers: List[str],
    data: List[List[str]],
    table_style: str = "default"
) -> Dict[str, Any]:
    """
    Create a formatted data table in Google Sheets.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_name: Name of the spreadsheet
        sheet_name: Name of the sheet to create table in
        headers: List of header strings
        data: 2D list of data rows
        table_style: Style of table ("default", "striped", "bordered")
    
    Returns:
        Dict containing table creation results
    """
    spreadsheet_id = get_spreadsheet_id_by_name(drive_service, spreadsheet_name)
    try:
        # Calculate table dimensions
        num_rows = len(data) + 1  # +1 for headers
        num_cols = len(headers)
        
        # Create the data to write (headers + data)
        table_data = [headers] + data
        
        # Determine the range
        end_col = chr(ord('A') + num_cols - 1)  # Convert number to letter
        range_name = f"{sheet_name}!A1:{end_col}{num_rows}"
        
        # Write the data
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body={'values': table_data}
        ).execute()
        
        # Prepare formatting requests
        requests = []
        
        # 1. Auto-resize columns
        auto_resize_request = {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,  # Assuming first sheet, should get actual sheet ID
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': num_cols
                }
            }
        }
        requests.append(auto_resize_request)
        
        # 2. Format header row (bold, background color)
        header_format_request = {
            'repeatCell': {
                'range': {
                    'sheetId': 0,  # Should get actual sheet ID
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': num_cols
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.2,
                            'blue': 0.2
                        },
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        }
        requests.append(header_format_request)
        
        # 3. Add borders to the entire table
        border_request = {
            'updateBorders': {
                'range': {
                    'sheetId': 0,  # Should get actual sheet ID
                    'startRowIndex': 0,
                    'endRowIndex': num_rows,
                    'startColumnIndex': 0,
                    'endColumnIndex': num_cols
                },
                'top': {
                    'style': 'SOLID',
                    'color': {'red': 0.5, 'green': 0.5, 'blue': 0.5}
                },
                'bottom': {
                    'style': 'SOLID',
                    'color': {'red': 0.5, 'green': 0.5, 'blue': 0.5}
                },
                'left': {
                    'style': 'SOLID',
                    'color': {'red': 0.5, 'green': 0.5, 'blue': 0.5}
                },
                'right': {
                    'style': 'SOLID',
                    'color': {'red': 0.5, 'green': 0.5, 'blue': 0.5}
                },
                'innerHorizontal': {
                    'style': 'SOLID',
                    'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
                },
                'innerVertical': {
                    'style': 'SOLID',
                    'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
                }
            }
        }
        requests.append(border_request)
        
        # 4. Add alternating row colors for striped style
        if table_style == "striped":
            for row_idx in range(1, num_rows, 2):  # Skip header row, alternate data rows
                stripe_request = {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,  # Should get actual sheet ID
                            'startRowIndex': row_idx,
                            'endRowIndex': row_idx + 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': num_cols
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.95,
                                    'green': 0.95,
                                    'blue': 0.95
                                }
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                }
                requests.append(stripe_request)
        
        # 5. Center-align all data cells
        data_align_request = {
            'repeatCell': {
                'range': {
                    'sheetId': 0,  # Should get actual sheet ID
                    'startRowIndex': 1,  # Data rows only
                    'endRowIndex': num_rows,
                    'startColumnIndex': 0,
                    'endColumnIndex': num_cols
                },
                'cell': {
                    'userEnteredFormat': {
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(horizontalAlignment,verticalAlignment)'
            }
        }
        requests.append(data_align_request)
        
        # Execute all formatting requests
        if requests:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
        
        return {
            "spreadsheet_name": spreadsheet_name,
            "sheet_name": sheet_name,
            "table_range": f"{sheet_name}!A1:{end_col}{num_rows}",
            "headers": headers,
            "data_rows": len(data),
            "total_cells": (len(data) + 1) * len(headers),
            "table_style": table_style,
            "message": f"Successfully created {table_style} data table with {len(headers)} columns and {len(data)} rows"
        }
        
    except HttpError as error:
        error_details = error.error_details[0] if hasattr(error, 'error_details') and error.error_details else {}
        error_message = error_details.get('message', str(error))
        raise RuntimeError(f"Error creating data table: {error_message}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error creating data table: {error}") 