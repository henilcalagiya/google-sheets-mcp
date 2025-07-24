# Google Sheets API v4 - All Available API Calls

## 📚 **Spreadsheets Resource**

### **GET /v4/spreadsheets/{spreadsheetId}**
Get spreadsheet metadata and properties

### **POST /v4/spreadsheets**
Create a new spreadsheet

### **PATCH /v4/spreadsheets/{spreadsheetId}**
Update spreadsheet properties (title, locale, timezone)

### **POST /v4/spreadsheets/{spreadsheetId}:batchUpdate**
Execute multiple operations in a single request

## 📊 **Values Resource**

### **GET /v4/spreadsheets/{spreadsheetId}/values/{range}**
Read cell values from a specific range

### **PUT /v4/spreadsheets/{spreadsheetId}/values/{range}**
Update cell values in a specific range

### **POST /v4/spreadsheets/{spreadsheetId}/values/{range}:append**
Append values to the end of a sheet

### **POST /v4/spreadsheets/{spreadsheetId}/values/{range}:clear**
Clear values from a specific range

### **GET /v4/spreadsheets/{spreadsheetId}/values:batchGet**
Read values from multiple ranges in a single request

### **POST /v4/spreadsheets/{spreadsheetId}/values:batchUpdate**
Update values in multiple ranges in a single request

## 📋 **Sheets Resource**

### **POST /v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo**
Copy a sheet to another spreadsheet

### **PATCH /v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}**
Update sheet properties (title, hidden, tab color)

## 📝 **DeveloperMetadata Resource**

### **GET /v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}**
Get developer metadata by ID

### **POST /v4/spreadsheets/{spreadsheetId}/developerMetadata:search**
Search for developer metadata

### **POST /v4/spreadsheets/{spreadsheetId}/developerMetadata**
Create new developer metadata

## 🔧 **Batch Operations (via batchUpdate)**

### **InsertDimension**
Insert rows or columns

### **DeleteDimension**
Delete rows or columns

### **UpdateDimensionProperties**
Update row/column properties (height, width, hidden)

### **InsertSheet**
Add a new sheet to the spreadsheet

### **DeleteSheet**
Remove a sheet from the spreadsheet

### **UpdateSheetProperties**
Update sheet properties (title, hidden, tab color)

### **CopyPaste**
Copy and paste data between ranges

### **CutPaste**
Cut and paste data between ranges

### **MergeCells**
Merge or unmerge cells

### **UnmergeCells**
Unmerge previously merged cells

### **UpdateBorders**
Update cell borders

### **UpdateCells**
Update cell data and formatting

### **AddChart**
Insert a chart

### **UpdateChartSpec**
Update chart specifications

### **DeleteChart**
Remove a chart

### **AddProtectedRange**
Add protection to a range of cells

### **UpdateProtectedRange**
Update range protection settings

### **DeleteProtectedRange**
Remove range protection

### **AutoResizeDimensions**
Automatically resize rows/columns to fit content

### **UpdateNamedRange**
Update a named range

### **DeleteNamedRange**
Remove a named range

### **AddConditionalFormatRule**
Add conditional formatting rule

### **UpdateConditionalFormatRule**
Update conditional formatting rule

### **DeleteConditionalFormatRule**
Remove conditional formatting rule

### **SortRange**
Sort data in a range

### **SetDataValidation**
Set data validation rules

### **ClearBasicFilter**
Clear basic filter from a range

### **AddBanding**
Add alternating row/column colors

### **UpdateBanding**
Update banding properties

### **DeleteBanding**
Remove banding

### **AddFilterView**
Add a filter view

### **UpdateFilterView**
Update filter view properties

### **DeleteFilterView**
Remove a filter view

### **AppendDimension**
Append rows or columns to the end

### **MoveDimension**
Move rows or columns to a new position

### **AddSlicer**
Add a slicer

### **UpdateSlicerSpec**
Update slicer specifications

### **DeleteSlicer**
Remove a slicer

### **AddDataSource**
Add a data source

### **UpdateDataSource**
Update data source properties

### **DeleteDataSource**
Remove a data source

### **RefreshDataSource**
Refresh data from external source

### **UpdateEmbeddedObjectPosition**
Update position of embedded objects

### **DeleteEmbeddedObject**
Remove embedded objects

### **UpdateDimensionGroup**
Update dimension group properties

### **DeleteDimensionGroup**
Remove dimension groups

### **CreateDeveloperMetadata**
Create developer metadata

### **UpdateDeveloperMetadata**
Update developer metadata

### **DeleteDeveloperMetadata**
Remove developer metadata

### **UpdateSpreadsheetProperties**
Update spreadsheet-level properties

### **UpdateSheetProperties**
Update sheet-level properties

### **UpdateGridProperties**
Update grid properties (row count, column count)

### **UpdateDimensionProperties**
Update dimension properties (width, height, hidden)

### **UpdateNamedRange**
Update named range properties

### **UpdateProtectedRange**
Update protected range properties

### **UpdateBasicFilter**
Update basic filter properties

### **UpdateConditionalFormatRule**
Update conditional format rule

### **UpdateChartSpec**
Update chart specifications

### **UpdateBanding**
Update banding properties

### **UpdateFilterView**
Update filter view properties

### **UpdateSlicerSpec**
Update slicer specifications

### **UpdateDataSource**
Update data source properties

### **UpdateEmbeddedObjectPosition**
Update embedded object position

### **UpdateDimensionGroup**
Update dimension group properties

### **UpdateDeveloperMetadata**
Update developer metadata

## 📊 **Total: 80+ API Operations Available**

This covers all the operations available in the Google Sheets API v4, from basic reading/writing to advanced features like charts, filters, and data validation. 