# Google Sheets API Tools Planning

## Overview
This document outlines the planning and development roadmap for Google Sheets API tools and their corresponding API requests.

## Spreadsheet Tools and Their API Requests ----------------------------------

### 1. Create spreadsheet
- **API Request**: `spreadsheets.create`
- **Status**: [ ] Not to do as of now 🔴
- **Priority**: High

### 2. Get spreadsheet metadata/properties
- **Tool Name**: `list_all_spreadsheets`
- **API Request**: `spreadsheets.get`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 3. Update spreadsheet properties
- **Tool Name**: `rename_spreadsheet_tool`
- **API Request**: `UpdateSpreadsheetPropertiesRequest` (in spreadsheets.batchUpdate)
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 4. Delete spreadsheet
- **API Request**: `drive.files.delete` (Handled via Google Drive API)
- **Status**: [ ] Not to do as of now 🔴
- **Priority**: Medium

### 5. List all sheets
- **Tool Name**: `list_sheets_tool`
- **API Request**: `spreadsheets.get`
- **Status**: [x] Implemented 🟢
- **Priority**: High

## Sheet (Tab) Tools and Their API Requests ----------------------------------

### 6. Add new sheet
- **Tool Name**: `add_sheets_tool`
- **API Request**: `AddSheetRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 7. Delete sheet
- **Tool Name**: `delete_sheets_tool`
- **API Request**: `DeleteSheetRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 8. Duplicate sheet
- **Tool Name**: `duplicate_sheet_tool`
- **API Request**: `DuplicateSheetRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 9. Get sheet properties
- **API Request**: `spreadsheets.get` (returns all sheet properties)
- **Status**: [ ] Not to do as of now 🔴
- **Priority**: High

### 10. Update sheet properties
- **Tool Name**: `rename_sheets_tool`
- **API Request**: `UpdateSheetPropertiesRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 11. Sort data on sheet
- **API Request**: `SortRangeRequest`
- **Status**: [ ] Not to do as of now 🔴
- **Priority**: Medium

### 12. Insert rows/columns
- **Tool Name**: `insert_sheet_dimension`
- **API Request**: `InsertDimensionRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 13. Delete rows/columns
- **Tool Name**: `delete_sheet_dimension`
- **API Request**: `DeleteDimensionRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 14. Move rows/columns
- **Tool Name**: `move_sheet_dimension`
- **API Request**: `MoveDimensionRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

## Cell/Range Tools and Their API Requests ----------------------------------

### 15. Get values
- **Tool Name**: `read_sheet_data_tool`
- **API Request**: `spreadsheets.values.get`, `spreadsheets.values.batchGet`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 16. Update values
- **API Request**: `spreadsheets.values.update`, `spreadsheets.values.batchUpdate`
- **Status**: [ ] On hold 🟡
- **Priority**: High

### 17. Clear values
- **API Request**: `spreadsheets.values.clear`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

### 18. Copy/paste
- **API Request**: `CopyPasteRequest`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

### 19. Merge/unmerge cells
- **API Request**: `MergeCellsRequest`, `UnmergeCellsRequest`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

### 20. Update formatting
- **API Request**: `UpdateCellsRequest`, `RepeatCellRequest`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

## Chart Tools and Their API Requests ----------------------------------

### 21. Add chart
- **Tool Name**: `create_chart_tool`
- **API Request**: `AddChartRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 22. Get chart metadata/properties
- **API Request**: `spreadsheets.get` (returns charts in sheet objects)
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 23. Update chart properties
- **API Request**: `UpdateChartSpecRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 24. Move chart
- **API Request**: `UpdateEmbeddedObjectPositionRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 25. Delete chart
- **API Request**: `DeleteEmbeddedObjectRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Table Tools and Their API Requests ----------------------------------

### 26. Add/create table
- **Tool Name**: `add_table_tool`
- **API Request**: `AddTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 27. Get table metadata/properties
- **Tool Name**: `get_table_metadata_tool`
- **API Request**: `spreadsheets.get` (includes tables list and metadata in sheet data)
- **Status**: [ ] Not implemented 🔴
- **Priority**: High

### 28. Update table properties
- **API Request**: `UpdateTableRequest`, `UpdateTableColumnRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 29. Delete table
- **Tool Name**: `delete_table_tool`
- **API Request**: `DeleteTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 30. Append rows to table
- **Tool Name**: `add_table_records_tool`
- **API Request**: `AppendCellsRequest` (with tableId)
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 31. Modify table ranges
- **Tool Name**: `modify_table_ranges_tool`
- **API Request**: `InsertRangeRequest`, `DeleteRangeRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 32. Set/update table data validation
- **API Request**: `SetDataValidationRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Low

## Named Range Tools and Their API Requests ----------------------------------

### 33. Add named range
- **API Request**: `AddNamedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 34. Get/list named ranges
- **API Request**: `spreadsheets.get` (returns all named ranges)
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 35. Update named range
- **API Request**: `UpdateNamedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 36. Delete named range
- **API Request**: `DeleteNamedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Developer Metadata Tools and Their API Requests ----------------------------------

### 37. Add metadata
- **API Request**: `CreateDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 38. Get/list metadata
- **API Request**: `GetDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 39. Update metadata
- **API Request**: `UpdateDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 40. Delete metadata
- **API Request**: `DeleteDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

## Filter and Filter View Tools and Their API Requests ----------------------------------

### 41. Add filter view
- **API Request**: `AddFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 42. Update filter view
- **API Request**: `UpdateFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 43. Delete filter view
- **API Request**: `DeleteFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 44. Duplicate filter view
- **API Request**: `DuplicateFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 45. Set/clear basic filter
- **API Request**: `SetBasicFilterRequest`, `ClearBasicFilterRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Protected Range Tools and Their API Requests ----------------------------------

### 46. Add protected range
- **API Request**: `AddProtectedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 47. Get/list protected ranges
- **API Request**: `spreadsheets.get` (returns protections)
- **Status**: [ ] Not implemented
- **Priority**: Low

### 48. Update protected range
- **API Request**: `UpdateProtectedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 49. Delete protected range
- **API Request**: `DeleteProtectedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

## Pivot Table Tools and Their API Requests ----------------------------------

### 50. Add pivot table
- **API Request**: `AddPivotTableRequest` (within sheet data update)
- **Status**: [ ] Not implemented
- **Priority**: Low

### 51. Get pivot table metadata
- **API Request**: `spreadsheets.get`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 52. Update pivot table
- **API Request**: `UpdateCellsRequest` (for pivot configuration)
- **Status**: [ ] Not implemented
- **Priority**: Low

### 53. Delete pivot table
- **API Request**: (Not a specific request—delete/clear range holding the pivot)
- **Status**: [ ] Not implemented
- **Priority**: Low

## Data Validation Tools and Their API Requests ----------------------------------

### 54. Set data validation
- **API Request**: `SetDataValidationRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 55. Clear data validation
- **API Request**: `SetDataValidationRequest` (with null/empty rule to clear)
- **Status**: [ ] Not implemented
- **Priority**: Low

## Conditional Formatting Tools and Their API Requests ----------------------------------

### 56. Add conditional format rule
- **API Request**: `AddConditionalFormatRuleRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 57. Update conditional format rule
- **API Request**: `UpdateConditionalFormatRuleRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 58. Delete conditional format rule
- **API Request**: `DeleteConditionalFormatRuleRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Embedded Object Tools and Their API Requests ----------------------------------

### 59. Add embedded object
- **API Request**: `AddEmbeddedObjectRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 60. Update embedded object
- **API Request**: `UpdateEmbeddedObjectPositionRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 61. Delete embedded object
- **API Request**: `DeleteEmbeddedObjectRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

## Additional Tools Already Implemented ----------------------------------

### Analysis Tools:
- **Tool Name**: `analyze_sheet_entities_tool`
- **API Request**: `spreadsheets.get` (with fields for analysis)
- **Status**: [x] Implemented 🟢
- **Description**: Analyze sheet structure and entities

### Search/Replace Tools:
- **Tool Name**: `find_replace`
- **API Request**: `FindReplaceRequest`
- **Status**: [x] Implemented 🟢
- **Description**: Find and replace text in ranges

### Formatting Tools:
- **Tool Name**: `resize_columns`
- **API Request**: `UpdateDimensionPropertiesRequest`
- **Status**: [x] Implemented 🟢
- **Description**: Resize column widths
