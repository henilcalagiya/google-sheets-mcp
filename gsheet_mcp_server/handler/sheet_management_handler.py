from typing import List, Dict, Any, Optional
from .api_functions import add_sheets, delete_sheets, list_sheets
from .read_sheet_data_handler import get_sheet_metadata
from gsheet_mcp_server.models import SheetInfo

def sheet_management_handler(
    sheets_service,
    spreadsheet_id: str,
    add_sheet_names: Optional[List[str]] = None,
    delete_sheet_ids: Optional[List[int]] = None,
    include_metadata: bool = True,
    target_sheet_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Sheet management with metadata support.
    
    Args:
        sheets_service: Google Sheets API service
        spreadsheet_id: ID of the spreadsheet
        add_sheet_names: List of sheet names to add (optional)
        delete_sheet_ids: List of sheet IDs to delete (optional)
        include_metadata: Whether to include detailed metadata
        target_sheet_names: List of specific sheet names to focus metadata on (optional)
    
    Returns:
        Dict containing sheet management results and metadata
    """
    
    # Perform sheet operations
    added_sheets = []
    deleted_ids = []
    
    if add_sheet_names:
        add_sheets(sheets_service, spreadsheet_id, add_sheet_names)
    
    if delete_sheet_ids:
        delete_sheets(sheets_service, spreadsheet_id, delete_sheet_ids)
        deleted_ids = delete_sheet_ids
    
    # Always get basic sheet list
    sheet_infos = list_sheets(sheets_service, spreadsheet_id)
    
    # Get added sheets info
    if add_sheet_names:
        for info in sheet_infos:
            if info.title in add_sheet_names:
                added_sheets.append(info)
    
    # Build message
    msg = []
    if added_sheets:
        msg.append(f"Added {len(added_sheets)} sheet(s)")
    if deleted_ids:
        msg.append(f"Deleted {len(deleted_ids)} sheet(s)")
    if not msg:
        msg.append("Listed sheets.")
    
    # Prepare response
    response = {
        "sheets": [s.model_dump() for s in sheet_infos],
        "added": [s.model_dump() for s in added_sheets],
        "deleted": deleted_ids,
        "message": ", ".join(msg),
        "operations_performed": {
            "sheets_added": len(added_sheets),
            "sheets_deleted": len(deleted_ids),
            "metadata_included": include_metadata
        }
    }
    
    # Add metadata if requested
    if include_metadata:
        try:
            if target_sheet_names and len(target_sheet_names) > 0:
                # Focus on specific sheets
                focused_metadata = []
                for sheet_name in target_sheet_names:
                    try:
                        metadata = get_sheet_metadata(
                            sheets_service=sheets_service,
                            spreadsheet_id=spreadsheet_id,
                            sheet_name=sheet_name
                        )
                        if 'sheet' in metadata:
                            focused_metadata.append(metadata['sheet'])
                    except Exception as e:
                        focused_metadata.append({
                            "sheet_name": sheet_name,
                            "error": str(e)
                        })
                
                response["metadata"] = {
                    "spreadsheet_id": spreadsheet_id,
                    "focused_sheets": focused_metadata,
                    "total_focused": len(focused_metadata)
                }
                response["message"] += f" Focused metadata for {len(target_sheet_names)} sheet(s)."
            else:
                # All sheets metadata
                metadata = get_sheet_metadata(
                    sheets_service=sheets_service,
                    spreadsheet_id=spreadsheet_id,
                    sheet_name=None
                )
                response["metadata"] = metadata
                response["message"] += " with metadata."
                
        except Exception as e:
            response["metadata_error"] = str(e)
            response["message"] += " (metadata retrieval failed)"
    
    return response 