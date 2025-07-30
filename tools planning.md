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

### 1. Add new sheet
- **Tool Name**: `add_sheets_tool`
- **API Request**: `AddSheetRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 2. Delete sheet
- **Tool Name**: `delete_sheets_tool`
- **API Request**: `DeleteSheetRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 3. Duplicate sheet
- **Tool Name**: `duplicate_sheet_tool`
- **API Request**: `DuplicateSheetRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 4. Get sheet properties
- **API Request**: `spreadsheets.get` (returns all sheet properties)
- **Status**: [ ] Not to do as of now 🔴
- **Priority**: High

### 5. Update sheet properties
- **Tool Name**: `rename_sheets_tool`
- **API Request**: `UpdateSheetPropertiesRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 6. Sort data on sheet
- **API Request**: `SortRangeRequest`
- **Status**: [ ] Not to do as of now 🔴
- **Priority**: Medium

### 7. Insert rows/columns
- **Tool Name**: `insert_sheet_dimension`
- **API Request**: `InsertDimensionRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 8. Delete rows/columns
- **Tool Name**: `delete_sheet_dimension`
- **API Request**: `DeleteDimensionRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 9. Move rows/columns
- **Tool Name**: `move_sheet_dimension`
- **API Request**: `MoveDimensionRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

## Cell/Range Tools and Their API Requests ----------------------------------

### 1. Get values
- **Tool Name**: `read_sheet_data_tool`
- **API Request**: `spreadsheets.values.get`, `spreadsheets.values.batchGet`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 2. Update values
- **API Request**: `spreadsheets.values.update`, `spreadsheets.values.batchUpdate`
- **Status**: [ ] On hold 🟡
- **Priority**: High

### 3. Clear values
- **API Request**: `spreadsheets.values.clear`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

### 4. Copy/paste
- **API Request**: `CopyPasteRequest`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

### 5. Merge/unmerge cells
- **API Request**: `MergeCellsRequest`, `UnmergeCellsRequest`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

### 6. Update formatting
- **API Request**: `UpdateCellsRequest`, `RepeatCellRequest`
- **Status**: [ ] On hold 🟡
- **Priority**: Medium

## Chart Tools and Their API Requests ----------------------------------

### 1. Add chart
- **Tool Name**: `create_chart_tool`
- **API Request**: `AddChartRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 2. Get chart metadata/properties
- **API Request**: `spreadsheets.get` (returns charts in sheet objects)
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 3. Update chart properties
- **API Request**: `UpdateChartSpecRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 4. Move chart
- **API Request**: `UpdateEmbeddedObjectPositionRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 5. Delete chart
- **API Request**: `DeleteEmbeddedObjectRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Table Tools and Their API Requests ----------------------------------

### 1. Create table
- **Tool Name**: `add_table_tool`
- **API Request**: `AddTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 2. Delete table
- **Tool Name**: `delete_table_tool`
- **API Request**: `DeleteTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 3. Get table metadata
- **Tool Name**: `get_table_metadata_tool`
- **API Request**: `spreadsheets.get` (includes tables list and metadata in sheet data)
- **Status**: [x] Implemented 🟢
- **Priority**: High
- **Description**: Retrieves comprehensive raw table metadata directly from Google Sheets API

### 4. Rename table
- **Tool Name**: `rename_table_tool`
- **API Request**: `UpdateTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium
- **Description**: Renames existing tables while preserving all data, formatting, and properties

### 5. Update table properties
- **Tool Name**: `update_table_properties_tool`
- **API Request**: `UpdateTableRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 6. Add table records
- **Tool Name**: `add_table_records_tool`
- **API Request**: `AppendCellsRequest` (with tableId)
- **Status**: [x] Implemented 🟢
- **Priority**: High

### 7. Delete table records
- **Tool Name**: `delete_table_records_tool`
- **API Request**: `DeleteDimensionRequest`, `ClearValuesRequest`, `UpdateTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 8. Update table records
- **Tool Name**: `update_table_records_tool`
- **API Request**: `UpdateCellsRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 9. Insert table records
- **Tool Name**: `insert_table_records_tool`
- **API Request**: `InsertDimensionRequest`, `UpdateCellsRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 10. Add table column
- **Tool Name**: `add_table_column_tool`
- **API Request**: `InsertDimensionRequest`, `UpdateTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 11. Delete table column
- **Tool Name**: `delete_table_column_tool`
- **API Request**: `DeleteDimensionRequest`, `UpdateTableRequest`
- **Status**: [x] Implemented 🟢
- **Priority**: Medium

### 12. Move table column
- **Tool Name**: `move_table_column_tool`
- **API Request**: `MoveDimensionRequest`, `UpdateTableRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Low

### 13. Update column properties
- **Tool Name**: `update_table_column_properties_tool`
- **API Request**: `UpdateTableColumnRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 14. Get table column metadata
- **Tool Name**: `get_table_column_metadata_tool`
- **API Request**: `spreadsheets.get` (includes table column properties)
- **Status**: [ ] Not implemented 🔴
- **Priority**: Low

### 15. Resize table range
- **Tool Name**: `resize_table_range_tool`
- **API Request**: `UpdateTableRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 16. Set table data validation
- **Tool Name**: `set_table_validation_tool`
- **API Request**: `SetDataValidationRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Low

### 17. Clear table data validation
- **Tool Name**: `clear_table_validation_tool`
- **API Request**: `SetDataValidationRequest` (with null/empty rule)
- **Status**: [ ] Not implemented 🔴
- **Priority**: Low

### 18. Merge table cells
- **Tool Name**: `merge_table_cells_tool`
- **API Request**: `MergeCellsRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Low

### 19. Unmerge table cells
- **Tool Name**: `unmerge_table_cells_tool`
- **API Request**: `UnmergeCellsRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Low

### 20. Sort table data
- **Tool Name**: `sort_table_data_tool`
- **API Request**: `SortRangeRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 21. Filter table data
- **Tool Name**: `filter_table_data_tool`
- **API Request**: `SetBasicFilterRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

### 22. Clear table filters
- **Tool Name**: `clear_table_filters_tool`
- **API Request**: `ClearBasicFilterRequest`
- **Status**: [ ] Not implemented 🔴
- **Priority**: Medium

## Named Range Tools and Their API Requests ----------------------------------

### 1. Add named range
- **API Request**: `AddNamedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 2. Get/list named ranges
- **API Request**: `spreadsheets.get` (returns all named ranges)
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 3. Update named range
- **API Request**: `UpdateNamedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 4. Delete named range
- **API Request**: `DeleteNamedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Developer Metadata Tools and Their API Requests ----------------------------------

### 1. Add metadata
- **API Request**: `CreateDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 2. Get/list metadata
- **API Request**: `GetDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 3. Update metadata
- **API Request**: `UpdateDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 4. Delete metadata
- **API Request**: `DeleteDeveloperMetadataRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

## Filter and Filter View Tools and Their API Requests ----------------------------------

### 1. Add filter view
- **API Request**: `AddFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 2. Update filter view
- **API Request**: `UpdateFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 3. Delete filter view
- **API Request**: `DeleteFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 4. Duplicate filter view
- **API Request**: `DuplicateFilterViewRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 5. Set/clear basic filter
- **API Request**: `SetBasicFilterRequest`, `ClearBasicFilterRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Protected Range Tools and Their API Requests ----------------------------------

### 1. Add protected range
- **API Request**: `AddProtectedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 2. Get/list protected ranges
- **API Request**: `spreadsheets.get` (returns protections)
- **Status**: [ ] Not implemented
- **Priority**: Low

### 3. Update protected range
- **API Request**: `UpdateProtectedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 4. Delete protected range
- **API Request**: `DeleteProtectedRangeRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

## Pivot Table Tools and Their API Requests ----------------------------------

### 1. Add pivot table
- **API Request**: `AddPivotTableRequest` (within sheet data update)
- **Status**: [ ] Not implemented
- **Priority**: Low

### 2. Get pivot table metadata
- **API Request**: `spreadsheets.get`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 3. Update pivot table
- **API Request**: `UpdateCellsRequest` (for pivot configuration)
- **Status**: [ ] Not implemented
- **Priority**: Low

### 4. Delete pivot table
- **API Request**: (Not a specific request—delete/clear range holding the pivot)
- **Status**: [ ] Not implemented
- **Priority**: Low

## Data Validation Tools and Their API Requests ----------------------------------

### 1. Set data validation
- **API Request**: `SetDataValidationRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 2. Clear data validation
- **API Request**: `SetDataValidationRequest` (with null/empty rule to clear)
- **Status**: [ ] Not implemented
- **Priority**: Low

## Conditional Formatting Tools and Their API Requests ----------------------------------

### 1. Add conditional format rule
- **API Request**: `AddConditionalFormatRuleRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 2. Update conditional format rule
- **API Request**: `UpdateConditionalFormatRuleRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

### 3. Delete conditional format rule
- **API Request**: `DeleteConditionalFormatRuleRequest`
- **Status**: [ ] Not implemented
- **Priority**: Medium

## Embedded Object Tools and Their API Requests ----------------------------------

### 1. Add embedded object
- **API Request**: `AddEmbeddedObjectRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 2. Update embedded object
- **API Request**: `UpdateEmbeddedObjectPositionRequest`
- **Status**: [ ] Not implemented
- **Priority**: Low

### 3. Delete embedded object
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
