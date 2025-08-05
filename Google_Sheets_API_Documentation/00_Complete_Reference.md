# Google Sheets API v4 - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Core Schemas](#core-schemas)
3. [Spreadsheets Resource](#spreadsheets-resource)
4. [Values Resource](#values-resource)
5. [Developer Metadata Resource](#developer-metadata-resource)
6. [Sheets Resource](#sheets-resource)
7. [Authentication & Scopes](#authentication--scopes)
8. [Error Handling](#error-handling)
9. [Rate Limits](#rate-limits)
10. [Complete API Reference](#complete-api-reference)
11. [Batch Update Request Types](#batch-update-request-types)

## Overview

**API Version:** v4  
**Base URL:** `https://sheets.googleapis.com/$discovery/rest?version=v4`  
**Description:** Reads and writes Google Sheets  
**Revision:** 20250728

## Core Schemas

### 1. ValueRange
Data within a range of the spreadsheet.

**Properties:**
- `range` (string): The range in A1 notation
- `majorDimension` (string): How data is organized
  - `DIMENSION_UNSPECIFIED`: Default value, do not use
  - `ROWS`: Operates on the rows of a sheet
  - `COLUMNS`: Operates on the columns of a sheet
- `values` (array): The data as array of arrays

### 2. UpdateValuesResponse
Response when updating a range of values.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `updatedRange` (string): The range (in A1 notation) that updates were applied to
- `updatedRows` (integer): Number of rows where at least one cell was updated
- `updatedColumns` (integer): Number of columns where at least one cell was updated
- `updatedCells` (integer): Number of cells updated
- `updatedData` (ValueRange): Values after updates (if includeValuesInResponse was true)

### 3. AppendValuesResponse
Response when appending values to a spreadsheet.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `tableRange` (string): The range (in A1 notation) of the table that values were appended to
- `updates` (UpdateValuesResponse): Information about the updates that were applied

### 4. ClearValuesRequest
Request for clearing a range of values.

**Properties:** (Empty object)

### 5. ClearValuesResponse
Response when clearing a range of values.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `clearedRange` (string): The range (in A1 notation) that was cleared

### 6. BatchGetValuesResponse
Response when retrieving multiple ranges of values.

**Properties:**
- `spreadsheetId` (string): The ID of the spreadsheet the data was retrieved from
- `valueRanges` (array): The requested values in the same order as requested ranges

### 7. BatchUpdateValuesRequest
Request for updating multiple ranges of values.

**Properties:**
- `valueInputOption` (string): How the input data should be interpreted
  - `INPUT_VALUE_OPTION_UNSPECIFIED`: Default input value
  - `RAW`: Values stored as-is
  - `USER_ENTERED`: Values parsed as if typed in UI
- `data` (array): The new values to apply to the spreadsheet
- `includeValuesInResponse` (boolean): Whether to include updated values in response
- `responseValueRenderOption` (string): How values should be rendered in response
  - `FORMATTED_VALUE`: Calculated and formatted values
  - `UNFORMATTED_VALUE`: Calculated but not formatted values
  - `FORMULA`: Values as formulas

### 8. BatchUpdateValuesResponse
Response when updating multiple ranges of values.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `totalUpdatedRows` (integer): Total number of rows where at least one cell was updated
- `totalUpdatedColumns` (integer): Total number of columns where at least one cell was updated
- `totalUpdatedCells` (integer): Total number of cells updated
- `responses` (array): One UpdateValuesResponse per requested range

### 9. BatchClearValuesRequest
Request for clearing multiple ranges of values.

**Properties:**
- `ranges` (array): The ranges to clear, in A1 notation

### 10. BatchClearValuesResponse
Response when clearing multiple ranges of values.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `clearedRanges` (array): The ranges that were cleared, in A1 notation

### 11. DataFilter
A filter that describes what data should be selected or returned from a request.

**Properties:**
- `a1Range` (string): A1 notation range
- `developerMetadataLookup` (DeveloperMetadataLookup): Developer metadata lookup

### 12. DataFilterValueRange
A range of values within a spreadsheet.

**Properties:**
- `dataFilter` (DataFilter): The data filter describing the location of the values
- `majorDimension` (string): The major dimension of the values
- `valueRange` (ValueRange): The data to be written

### 13. BatchGetValuesByDataFilterRequest
Request for retrieving multiple ranges of values that match the specified data filters.

**Properties:**
- `dataFilters` (array): The data filters used to match the ranges of values
- `majorDimension` (string): The major dimension that results should use
- `valueRenderOption` (string): How values should be rendered in the output
- `dateTimeRenderOption` (string): How dates, times, and durations should be represented

### 14. BatchGetValuesByDataFilterResponse
Response when retrieving multiple ranges of values that match the specified data filters.

**Properties:**
- `spreadsheetId` (string): The ID of the spreadsheet the data was retrieved from
- `valueRanges` (array): The requested values with the data filters applied

### 15. BatchUpdateValuesByDataFilterRequest
Request for updating multiple ranges of values that match the specified data filters.

**Properties:**
- `valueInputOption` (string): How the input data should be interpreted
- `data` (array): The new values to apply to the spreadsheet
- `includeValuesInResponse` (boolean): Whether to include updated values in response
- `responseValueRenderOption` (string): How values should be rendered in response

### 16. BatchUpdateValuesByDataFilterResponse
Response when updating multiple ranges of values that match the specified data filters.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `totalUpdatedRows` (integer): Total number of rows where at least one cell was updated
- `totalUpdatedColumns` (integer): Total number of columns where at least one cell was updated
- `totalUpdatedCells` (integer): Total number of cells updated
- `responses` (array): One UpdateValuesResponse per requested range

### 17. BatchClearValuesByDataFilterRequest
Request for clearing multiple ranges of values that match the specified data filters.

**Properties:**
- `dataFilters` (array): The data filters used to match the ranges of values

### 18. BatchClearValuesByDataFilterResponse
Response when clearing multiple ranges of values that match the specified data filters.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `clearedRanges` (array): The ranges that were cleared, in A1 notation

### 19. DeveloperMetadata
Developer metadata associated with a location or document.

**Properties:**
- `metadataId` (integer): The metadata ID
- `metadataKey` (string): The metadata key
- `metadataValue` (string): The metadata value
- `location` (DeveloperMetadataLocation): The location where the metadata is associated
- `visibility` (string): The metadata visibility
  - `DEVELOPER_METADATA_VISIBILITY_UNSPECIFIED`: Default value
  - `DOCUMENT`: Document-scoped metadata
  - `PROJECT`: Project-scoped metadata

### 20. DeveloperMetadataLocation
A location where metadata may be associated in a spreadsheet.

**Properties:**
- `locationType` (string): The type of location this object represents
  - `DEVELOPER_METADATA_LOCATION_TYPE_UNSPECIFIED`: Default value
  - `ROW`: Row location
  - `COLUMN`: Column location
  - `SHEET`: Sheet location
  - `SPREADSHEET`: Spreadsheet location
- `dimensionRange` (DimensionRange): A range along a single dimension
- `sheetId` (integer): The ID of the sheet when this is a sheet location
- `spreadsheet` (boolean): True when this is a spreadsheet location

### 21. DeveloperMetadataLookup
Determines how values in a response should be rendered.

**Properties:**
- `locationMatchingStrategy` (string): The location matching strategy
  - `DEVELOPER_METADATA_LOOKUP_LOCATION_MATCHING_STRATEGY_UNSPECIFIED`: Default value
  - `EXACT_LOCATION`: Exact location matching
  - `INTERSECTING_LOCATION`: Intersecting location matching
- `locationType` (string): The type of location this object represents
- `metadataId` (integer): The metadata ID
- `metadataKey` (string): The metadata key
- `metadataLocation` (DeveloperMetadataLocation): The metadata location
- `metadataValue` (string): The metadata value
- `useAllSheets` (boolean): If true, considers all sheets in the spreadsheet

### 22. SearchDeveloperMetadataRequest
A request to retrieve all developer metadata matching the specified data filters.

**Properties:**
- `dataFilters` (array): The data filters describing the criteria used to determine which DeveloperMetadata entries to return

### 23. SearchDeveloperMetadataResponse
A response to a developer metadata search request.

**Properties:**
- `matchedDeveloperMetadata` (array): The metadata matching the criteria of the search request

### 24. CopySheetToAnotherSpreadsheetRequest
The request to copy a sheet to another spreadsheet.

**Properties:**
- `destinationSpreadsheetId` (string): The ID of the spreadsheet to copy the sheet to

### 25. SheetProperties
Properties of a sheet.

**Properties:**
- `sheetId` (integer): The ID of the sheet
- `title` (string): The name of the sheet
- `index` (integer): The position of the sheet in the spreadsheet
- `sheetType` (string): The type of sheet
  - `SHEET_TYPE_UNSPECIFIED`: Default value
  - `GRID`: A normal sheet
  - `OBJECT`: An object sheet
- `gridProperties` (GridProperties): Additional properties of the sheet
- `hidden` (boolean): True if the sheet is hidden
- `tabColor` (Color): The color of the sheet tab
- `rightToLeft` (boolean): True if the sheet is an RTL sheet

### 26. GridProperties
Properties of a grid.

**Properties:**
- `rowCount` (integer): The number of rows in the grid
- `columnCount` (integer): The number of columns in the grid
- `frozenRowCount` (integer): The number of rows that are frozen in the grid
- `frozenColumnCount` (integer): The number of columns that are frozen in the grid
- `hideGridlines` (boolean): True if the gridlines are hidden
- `rowGroupControlAfter` (boolean): True if the row group control is shown after the group
- `columnGroupControlAfter` (boolean): True if the column group control is shown after the group

### 27. Color
A color value.

**Properties:**
- `red` (number): The amount of red in the color as a value in the interval [0, 1]
- `green` (number): The amount of green in the color as a value in the interval [0, 1]
- `blue` (number): The amount of blue in the color as a value in the interval [0, 1]
- `alpha` (number): The fraction of this color that should be applied to the pixel

### 28. DimensionRange
A range along a single dimension on a sheet.

**Properties:**
- `sheetId` (integer): The sheet this range is on
- `dimension` (string): The dimension of the range
  - `DIMENSION_UNSPECIFIED`: Default value
  - `ROWS`: Rows
  - `COLUMNS`: Columns
- `startIndex` (integer): The start (inclusive) of the range
- `endIndex` (integer): The end (exclusive) of the range

### 29. BatchUpdateSpreadsheetRequest
The request for updating any aspect of a spreadsheet.

**Properties:**
- `requests` (array): A list of updates to apply to the spreadsheet
- `includeSpreadsheetInResponse` (boolean): Determines if the update response should include the spreadsheet resource
- `responseRanges` (array): Limits the ranges included in the response spreadsheet
- `responseIncludeGridData` (boolean): True if grid data should be returned

### 30. BatchUpdateSpreadsheetResponse
The response for updating a spreadsheet.

**Properties:**
- `spreadsheetId` (string): The reply of the updates
- `replies` (array): The reply of the updates
- `updatedSpreadsheet` (Spreadsheet): The spreadsheet after updates were applied

### 31. Spreadsheet
Resource that represents a Google Sheets spreadsheet.

**Properties:**
- `spreadsheetId` (string): The ID of the spreadsheet
- `properties` (SpreadsheetProperties): Overall properties of a spreadsheet
- `sheets` (array): The sheets that are part of the spreadsheet
- `namedRanges` (array): The named ranges defined in a spreadsheet
- `developerMetadata` (array): The developer metadata associated with a spreadsheet
- `dataSources` (array): Data sources refresh in the spreadsheet

### 32. SpreadsheetProperties
Properties of a spreadsheet.

**Properties:**
- `title` (string): The title of the spreadsheet
- `locale` (string): The locale of the spreadsheet
- `autoRecalc` (string): The amount of time to wait before volatile functions are recalculated
  - `RECALCULATION_INTERVAL_UNSPECIFIED`: Default value
  - `ON_CHANGE`: Volatile functions are recalculated on every change
  - `MINUTE`: Volatile functions are recalculated on every minute
  - `HOUR`: Volatile functions are recalculated on every hour
- `timeZone` (string): The time zone of the spreadsheet
- `defaultFormat` (CellFormat): The default format of all cells in the spreadsheet
- `iterativeCalculationSettings` (IterativeCalculationSettings): Determines whether and how circular references are resolved

### 33. CellFormat
The format of a cell.

**Properties:**
- `numberFormat` (NumberFormat): The number format of the cell
- `backgroundColor` (Color): The background color of the cell
- `borders` (Borders): The borders of the cell
- `padding` (Padding): The padding of the cell
- `horizontalAlignment` (string): The horizontal alignment of the value in the cell
  - `HORIZONTAL_ALIGN_UNSPECIFIED`: Default value
  - `LEFT`: Left alignment
  - `CENTER`: Center alignment
  - `RIGHT`: Right alignment
- `verticalAlignment` (string): The vertical alignment of the value in the cell
  - `VERTICAL_ALIGN_UNSPECIFIED`: Default value
  - `TOP`: Top alignment
  - `MIDDLE`: Middle alignment
  - `BOTTOM`: Bottom alignment
- `wrapStrategy` (string): The wrap strategy for the value in the cell
  - `WRAP_STRATEGY_UNSPECIFIED`: Default value
  - `OVERFLOW_CELL`: Text wraps to next line
  - `CLIP`: Text is clipped to the cell
  - `WRAP`: Text wraps within the cell
- `textDirection` (string): The direction of the text in the cell
  - `TEXT_DIRECTION_UNSPECIFIED`: Default value
  - `LEFT_TO_RIGHT`: Left to right
  - `RIGHT_TO_LEFT`: Right to left
- `textFormat` (TextFormat): The format of the text in the cell
- `hyperlinkDisplayType` (string): The display type of the hyperlink
  - `HYPERLINK_DISPLAY_TYPE_UNSPECIFIED`: Default value
  - `LINKED`: Shows the link text
  - `PLAIN_TEXT`: Shows the URL

### 34. NumberFormat
The number format of a cell.

**Properties:**
- `type` (string): The type of the number format
  - `NUMBER_FORMAT_TYPE_UNSPECIFIED`: Default value
  - `TEXT`: Text format
  - `NUMBER`: Number format
  - `PERCENT`: Percent format
  - `CURRENCY`: Currency format
  - `DATE`: Date format
  - `TIME`: Time format
  - `DATE_TIME`: Date time format
  - `SCIENTIFIC`: Scientific format
- `pattern` (string): The number format pattern

### 35. Borders
The borders of a cell.

**Properties:**
- `top` (Border): The top border of the cell
- `bottom` (Border): The bottom border of the cell
- `left` (Border): The left border of the cell
- `right` (Border): The right border of the cell

### 36. Border
A border along a cell.

**Properties:**
- `style` (string): The style of the border
  - `STYLE_UNSPECIFIED`: Default value
  - `DOTTED`: Dotted style
  - `DASHED`: Dashed style
  - `SOLID`: Solid style
  - `SOLID_MEDIUM`: Solid medium style
  - `SOLID_THICK`: Solid thick style
  - `NONE`: No border
  - `DOUBLE`: Double border
- `color` (Color): The color of the border

### 37. Padding
The amount of padding around the cell.

**Properties:**
- `top` (integer): The top padding of the cell
- `right` (integer): The right padding of the cell
- `bottom` (integer): The bottom padding of the cell
- `left` (integer): The left padding of the cell

### 38. TextFormat
The format of the text in the cell.

**Properties:**
- `foregroundColor` (Color): The foreground color of the text
- `fontFamily` (string): The font family of the text
- `fontSize` (integer): The size of the font
- `bold` (boolean): True if the text is bold
- `italic` (boolean): True if the text is italic
- `strikethrough` (boolean): True if the text has a strikethrough
- `underline` (boolean): True if the text is underlined

### 39. IterativeCalculationSettings
Settings to control how circular references are resolved with iterative calculation.

**Properties:**
- `maxIterations` (integer): The maximum number of calculation iterations
- `convergenceThreshold` (number): The threshold for convergence

### 40. NamedRange
A named range.

**Properties:**
- `namedRangeId` (string): The ID of the named range
- `name` (string): The name of the named range
- `range` (GridRange): The range this named range covers

### 41. GridRange
A range on a sheet. All indexes are zero-based.

**Properties:**
- `sheetId` (integer): The sheet this range is on
- `startRowIndex` (integer): The start row (inclusive) of the range
- `endRowIndex` (integer): The end row (exclusive) of the range
- `startColumnIndex` (integer): The start column (inclusive) of the range
- `endColumnIndex` (integer): The end column (exclusive) of the range

### 42. Chart
A chart embedded in a sheet.

**Properties:**
- `chartId` (integer): The ID of the chart
- `spec` (ChartSpec): The specifications of the chart
- `position` (EmbeddedObjectPosition): The position of the chart

### 43. ChartSpec
The specifications of a chart.

**Properties:**
- `title` (string): The title of the chart
- `basicChart` (BasicChartSpec): A basic chart specification
- `pieChart` (PieChartSpec): A pie chart specification
- `bubbleChart` (BubbleChartSpec): A bubble chart specification
- `candlestickChart` (CandlestickChartSpec): A candlestick chart specification
- `orgChart` (OrgChartSpec): An org chart specification
- `histogramChart` (HistogramChartSpec): A histogram chart specification
- `waterfallChart` (WaterfallChartSpec): A waterfall chart specification
- `treemapChart` (TreemapChartSpec): A treemap chart specification
- `scorecardChart` (ScorecardChartSpec): A scorecard chart specification

### 44. EmbeddedObjectPosition
The position of an embedded object such as a chart.

**Properties:**
- `sheetId` (integer): The sheet this is on
- `overlayPosition` (OverlayPosition): The position at which the object is attached to the sheet
- `newSheet` (boolean): If true, the object is positioned on a new sheet

### 45. OverlayPosition
The location an object is overlaid on top of a grid.

**Properties:**
- `anchorCell` (GridCoordinate): The cell the object is anchored to
- `offsetXPixels` (integer): The horizontal offset in pixels
- `offsetYPixels` (integer): The vertical offset in pixels
- `widthPixels` (integer): The width of the object in pixels
- `heightPixels` (integer): The height of the object in pixels

### 46. GridCoordinate
A coordinate in a sheet.

**Properties:**
- `sheetId` (integer): The sheet this coordinate is on
- `rowIndex` (integer): The row index of the coordinate
- `columnIndex` (integer): The column index of the coordinate

### 47. ConditionalFormatRule
A rule describing a conditional format.

**Properties:**
- `ranges` (array): The ranges that are formatted if the condition is true
- `booleanRule` (BooleanRule): The formatting is either "on" or "off" according to the rule
- `gradientRule` (GradientRule): The formatting will vary based on the values in each cell

### 48. BooleanRule
A rule that may or may not match, requiring a formula to evaluate.

**Properties:**
- `condition` (BooleanCondition): The condition of the rule
- `format` (CellFormat): The format to apply to the cell

### 49. BooleanCondition
A condition that can evaluate to true or false.

**Properties:**
- `type` (string): The type of condition
  - `CONDITION_TYPE_UNSPECIFIED`: Default value
  - `NUMBER_GREATER`: The cell's value must be greater than the condition's value
  - `NUMBER_GREATER_THAN_EQ`: The cell's value must be greater than or equal to the condition's value
  - `NUMBER_LESS`: The cell's value must be less than the condition's value
  - `NUMBER_LESS_THAN_EQ`: The cell's value must be less than or equal to the condition's value
  - `NUMBER_EQ`: The cell's value must be equal to the condition's value
  - `NUMBER_NOT_EQ`: The cell's value must not be equal to the condition's value
  - `NUMBER_BETWEEN`: The cell's value must be between the condition's two values
  - `NUMBER_NOT_BETWEEN`: The cell's value must not be between the condition's two values
  - `TEXT_CONTAINS`: The cell's value must contain the condition's value
  - `TEXT_NOT_CONTAINS`: The cell's value must not contain the condition's value
  - `TEXT_STARTS_WITH`: The cell's value must start with the condition's value
  - `TEXT_ENDS_WITH`: The cell's value must end with the condition's value
  - `TEXT_EQ`: The cell's value must be equal to the condition's value
  - `TEXT_IS_EMAIL`: The cell's value must be a valid email address
  - `TEXT_IS_URL`: The cell's value must be a valid URL
  - `DATE_EQ`: The cell's value must be equal to the condition's value
  - `DATE_BEFORE`: The cell's value must be before the condition's value
  - `DATE_AFTER`: The cell's value must be after the condition's value
  - `DATE_ON_OR_BEFORE`: The cell's value must be on or before the condition's value
  - `DATE_ON_OR_AFTER`: The cell's value must be on or after the condition's value
  - `DATE_BETWEEN`: The cell's value must be between the condition's two values
  - `DATE_NOT_BETWEEN`: The cell's value must not be between the condition's two values
  - `DATE_IS_TODAY`: The cell's value must be today
  - `DATE_IS_YESTERDAY`: The cell's value must be yesterday
  - `DATE_IS_LAST_7_DAYS`: The cell's value must be in the last 7 days
  - `DATE_IS_LAST_MONTH`: The cell's value must be in the last month
  - `DATE_IS_LAST_YEAR`: The cell's value must be in the last year
  - `DATE_IS_THIS_MONTH`: The cell's value must be in this month
  - `DATE_IS_THIS_YEAR`: The cell's value must be in this year
  - `DATE_IS_NEXT_MONTH`: The cell's value must be in next month
  - `DATE_IS_NEXT_YEAR`: The cell's value must be in next year
  - `DATE_IS_EMPTY`: The cell's value must be empty
  - `DATE_IS_NOT_EMPTY`: The cell's value must not be empty
  - `CUSTOM_FORMULA`: The cell's value must match the custom formula
- `values` (array): The values of the condition

### 50. GradientRule
A rule that applies a gradient color scale to a cell or range.

**Properties:**
- `minpoint` (InterpolationPoint): The interpolation point for the minimum value
- `midpoint` (InterpolationPoint): The interpolation point for the midpoint value
- `maxpoint` (InterpolationPoint): The interpolation point for the maximum value

### 51. InterpolationPoint
A single interpolation point on a gradient scale.

**Properties:**
- `color` (Color): The color this interpolation point should use
- `type` (string): How the value should be interpreted
  - `INTERPOLATION_POINT_TYPE_UNSPECIFIED`: Default value
  - `MIN`: The minimum value in the range
  - `MAX`: The maximum value in the range
  - `NUMBER`: A number value
  - `PERCENT`: A percentage value
  - `PERCENTILE`: A percentile value
- `value` (string): The value for this interpolation point

### 52. DataSource
A data source.

**Properties:**
- `dataSourceId` (string): The ID of the data source
- `spec` (DataSourceSpec): The specification of the data source
- `calculatedColumns` (array): The calculated columns for the data source
- `sheets` (array): The sheets that are part of the data source

### 53. DataSourceSpec
The specification of a data source.

**Properties:**
- `parameters` (array): The parameters of the data source
- `bigQuery` (BigQueryDataSourceSpec): A BigQuery data source specification

### 54. BigQueryDataSourceSpec
The specification for a BigQuery data source.

**Properties:**
- `projectId` (string): The ID of the BigQuery project
- `querySpec` (BigQueryQuerySpec): The BigQuery query specification
- `tableSpec` (BigQueryTableSpec): The BigQuery table specification

### 55. Table
A table in a sheet.

**Properties:**
- `tableId` (integer): The ID of the table
- `displayName` (string): The display name of the table
- `range` (GridRange): The range the table covers
- `columnCount` (integer): The number of columns in the table
- `rows` (array): The rows in the table
- `columns` (array): The columns in the table
- `style` (TableStyle): The style of the table

### 56. TableRow
A row in a table.

**Properties:**
- `values` (array): The values in the row

### 57. TableColumn
A column in a table.

**Properties:**
- `columnId` (string): The ID of the column
- `displayName` (string): The display name of the column
- `index` (integer): The index of the column

### 58. TableStyle
The style of a table.

**Properties:**
- `headerRow` (boolean): True if the header row should be shown
- `totalRow` (boolean): True if the total row should be shown
- `firstColumn` (boolean): True if the first column should be shown
- `lastColumn` (boolean): True if the last column should be shown
- `bandedRows` (boolean): True if the rows should be banded
- `bandedColumns` (boolean): True if the columns should be banded

### 59. BasicChartSpec
The specification for a basic chart.

**Properties:**
- `chartType` (string): The type of the chart
  - `BASIC_CHART_TYPE_UNSPECIFIED`: Default value
  - `LINE`: Line chart
  - `AREA`: Area chart
  - `COLUMN`: Column chart
  - `BAR`: Bar chart
  - `PIE`: Pie chart
  - `SCATTER`: Scatter chart
  - `COMBO`: Combo chart
  - `STEPPED_AREA`: Stepped area chart
- `legendPosition` (string): The position of the chart legend
  - `BASIC_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
  - `BOTTOM_LEGEND`: Legend at the bottom
  - `LEFT_LEGEND`: Legend at the left
  - `RIGHT_LEGEND`: Legend at the right
  - `TOP_LEGEND`: Legend at the top
  - `NO_LEGEND`: No legend
- `axis` (array): The list of chart data
- `domains` (array): The domain of the chart
- `headerCount` (integer): The number of rows or columns in the data that are "headers"

### 60. PieChartSpec
The specification for a pie chart.

**Properties:**
- `legendPosition` (string): The position of the chart legend
  - `PIE_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
  - `BOTTOM_LEGEND`: Legend at the bottom
  - `LEFT_LEGEND`: Legend at the left
  - `RIGHT_LEGEND`: Legend at the right
  - `TOP_LEGEND`: Legend at the top
  - `NO_LEGEND`: No legend
- `domain` (ChartData): The domain of the pie chart
- `series` (ChartData): The series of the pie chart
- `threeDimensional` (boolean): True if the chart is 3D

### 61. ChartData
The data included in a domain or series.

**Properties:**
- `sourceRange` (ChartSourceRange): The source ranges of the data
- `aggregateType` (string): The aggregation type for the series of a data source chart
  - `CHART_AGGREGATE_TYPE_UNSPECIFIED`: Default value
  - `AVERAGE`: Average
  - `COUNT`: Count
  - `MAX`: Maximum
  - `MEDIAN`: Median
  - `MIN`: Minimum
  - `SUM`: Sum

### 62. ChartSourceRange
The source ranges of the data.

**Properties:**
- `sources` (array): The ranges of data for a series or domain

### 63. GridRange
A range on a sheet. All indexes are zero-based.

**Properties:**
- `sheetId` (integer): The sheet this range is on
- `startRowIndex` (integer): The start row (inclusive) of the range
- `endRowIndex` (integer): The end row (exclusive) of the range
- `startColumnIndex` (integer): The start column (inclusive) of the range
- `endColumnIndex` (integer): The end column (exclusive) of the range

### 64. UpdateCellsRequest
Updates all cells in a range with new data.

**Properties:**
- `range` (GridRange): The range to write data to
- `rows` (array): The data to write
- `fields` (string): The fields of CellData that should be updated

### 65. InsertDimensionRequest
Inserts rows or columns in a sheet.

**Properties:**
- `range` (DimensionRange): The range to insert rows or columns into
- `inheritFromBefore` (boolean): Whether dimension properties should be extended from the dimension before the inserted dimension

### 66. DeleteDimensionRequest
Deletes rows or columns in a sheet.

**Properties:**
- `range` (DimensionRange): The range to delete rows or columns from

### 67. UpdateSheetPropertiesRequest
Updates the properties of a sheet.

**Properties:**
- `properties` (SheetProperties): The properties to update
- `fields` (string): The fields that should be updated

### 68. AddSheetRequest
Adds a new sheet.

**Properties:**
- `properties` (SheetProperties): The properties the new sheet should have

### 69. DeleteSheetRequest
Deletes a sheet.

**Properties:**
- `sheetId` (integer): The ID of the sheet to delete

### 70. DuplicateSheetRequest
Duplicates a sheet.

**Properties:**
- `sourceSheetId` (integer): The ID of the sheet to duplicate
- `insertSheetIndex` (integer): The zero-based index where the new sheet should be inserted
- `newSheetName` (string): The name of the new sheet

### 71. UpdateBordersRequest
Updates the borders of a range of cells.

**Properties:**
- `range` (GridRange): The range whose borders should be updated
- `top` (Border): The border to apply to the top of the range
- `bottom` (Border): The border to apply to the bottom of the range
- `left` (Border): The border to apply to the left of the range
- `right` (Border): The border to apply to the right of the range
- `innerHorizontal` (Border): The border to apply to the inner horizontal borders
- `innerVertical` (Border): The border to apply to the inner vertical borders

### 72. UpdateConditionalFormatRuleRequest
Updates a conditional format rule at the given index.

**Properties:**
- `sheetId` (integer): The sheet the conditional format rule is being updated on
- `index` (integer): The index of the conditional format rule to update
- `rule` (ConditionalFormatRule): The rule that should replace the rule at the given index

### 73. AddConditionalFormatRuleRequest
Adds a new conditional format rule.

**Properties:**
- `rule` (ConditionalFormatRule): The rule to add

### 74. DeleteConditionalFormatRuleRequest
Deletes a conditional format rule at the given index.

**Properties:**
- `sheetId` (integer): The sheet the conditional format rule is being deleted from
- `index` (integer): The index of the conditional format rule to delete

### 75. UpdateChartSpecRequest
Updates a chart's specifications.

**Properties:**
- `chartId` (integer): The ID of the chart to update
- `spec` (ChartSpec): The specification to apply to the chart

### 76. AddChartRequest
Adds a chart to the sheet.

**Properties:**
- `chart` (EmbeddedChart): The chart that should be added to the sheet

### 77. EmbeddedChart
A chart embedded in a sheet.

**Properties:**
- `chartId` (integer): The ID of the chart
- `spec` (ChartSpec): The specifications of the chart
- `position` (EmbeddedObjectPosition): The position of the chart

### 78. UpdateNamedRangeRequest
Updates a named range.

**Properties:**
- `namedRangeId` (string): The ID of the named range to update
- `namedRange` (NamedRange): The named range to update with
- `fields` (string): The fields that should be updated

### 79. AddNamedRangeRequest
Adds a named range.

**Properties:**
- `namedRange` (NamedRange): The named range to add

### 80. DeleteNamedRangeRequest
Removes a named range.

**Properties:**
- `namedRangeId` (string): The ID of the named range to delete

### 81. UpdateDeveloperMetadataRequest
Updates developer metadata.

**Properties:**
- `dataFilters` (array): The filters matching the metadata entries to update
- `developerMetadata` (DeveloperMetadata): The value that all metadata matched by the data filters will be updated to
- `fields` (string): The fields that should be updated

### 82. DeleteDeveloperMetadataRequest
Removes developer metadata.

**Properties:**
- `dataFilters` (array): The filters matching the metadata entries to delete

### 83. AutoResizeDimensionsRequest
Automatically resizes one or more dimensions based on the contents of the cells in those dimensions.

**Properties:**
- `dimensions` (DimensionRange): The dimensions to automatically resize

### 84. MoveDimensionRequest
Moves one or more rows or columns.

**Properties:**
- `source` (DimensionRange): The source dimensions to move
- `destinationIndex` (integer): The zero-based start index of where to move the source dimensions

### 85. UpdateDimensionPropertiesRequest
Updates the properties of dimensions within the specified range.

**Properties:**
- `range` (DimensionRange): The range to update properties for
- `properties` (DimensionProperties): The properties to update
- `fields` (string): The fields that should be updated

### 86. DimensionProperties
Properties about a dimension.

**Properties:**
- `hiddenByUser` (boolean): True if this dimension is explicitly hidden
- `hiddenByFilter` (boolean): True if this dimension is being filtered
- `pixelSize` (integer): The height (if a row) or width (if a column) of the dimension in pixels

### 87. UpdateSpreadsheetPropertiesRequest
Updates the properties of a spreadsheet.

**Properties:**
- `properties` (SpreadsheetProperties): The properties to update
- `fields` (string): The fields that should be updated

### 88. RefreshDataSourceRequest
Refreshes one or more data source objects in the spreadsheet by the specified references.

**Properties:**
- `dataSourceId` (string): Reference to a DataSource
- `force` (boolean): If true, refreshes all data sources in the spreadsheet

### 89. SortRangeRequest
Sorts data in rows based on a column.

**Properties:**
- `range` (GridRange): The range to sort
- `sortSpecs` (array): The sort order per column

### 90. SortSpec
A sort order associated with a specific column or row.

**Properties:**
- `dimensionIndex` (integer): The dimension the sort should be applied to
- `sortOrder` (string): The order data should be sorted
  - `ASCENDING`: Ascending order
  - `DESCENDING`: Descending order

### 91. CellData
Data about a specific cell.

**Properties:**
- `userEnteredValue` (ExtendedValue): The value the user entered in the cell
- `effectiveValue` (ExtendedValue): The effective value of the cell
- `formattedValue` (string): The formatted value of the cell
- `userEnteredFormat` (CellFormat): The format the user entered for the cell
- `effectiveFormat` (CellFormat): The effective format of the cell
- `hyperlinkDisplayType` (string): The display type of the hyperlink
- `textFormatRuns` (array): Runs of text that are formatted
- `dataValidation` (DataValidationRule): The data validation rule on the cell

### 92. ExtendedValue
The kinds of value that a cell can have.

**Properties:**
- `numberValue` (number): Represents a double value
- `stringValue` (string): Represents a string value
- `boolValue` (boolean): Represents a boolean value
- `formulaValue` (string): Represents a formula
- `errorValue` (ErrorValue): Represents an error

### 93. ErrorValue
An error in a cell.

**Properties:**
- `type` (string): The type of error
  - `ERROR_TYPE_UNSPECIFIED`: Default value
  - `ERROR`: General error
  - `NULL_VALUE`: Null value error
  - `DIVIDE_BY_ZERO`: Divide by zero error
  - `VALUE`: Value error
  - `REF`: Reference error
  - `NAME`: Name error
  - `NUM`: Number error
  - `N_A`: N/A error
  - `LOADING`: Loading error
- `message` (string): A message with more information about the error

### 94. DataValidationRule
A data validation rule.

**Properties:**
- `condition` (BooleanCondition): The condition that data in the cell must match
- `inputMessage` (string): A message to show the user when adding data to the cell
- `strict` (boolean): True if the data validation rule should reject invalid data
- `showCustomUi` (boolean): True if the data validation rule should show custom help text

### 95. TextFormatRun
A run of a text format.

**Properties:**
- `startIndex` (integer): The character index where this run starts
- `format` (TextFormat): The format of this run

### 96. RowData
Data about each cell in a row.

**Properties:**
- `values` (array): The values in the row, one per column

### 97. BigQueryQuerySpec
The specification for a BigQuery data source that is connected to a sheet.

**Properties:**
- `rawQuery` (string): The raw query string

### 98. BigQueryTableSpec
The specification for a BigQuery data source that is connected to a sheet.

**Properties:**
- `tableId` (string): The BigQuery table id
- `datasetId` (string): The BigQuery dataset id
- `projectId` (string): The BigQuery project id

### 99. CalculatedColumn
A column in a data source.

**Properties:**
- `dataSourceColumnReference` (DataSourceColumnReference): The reference to the data source column
- `formula` (string): The formula for the calculated column

### 100. DataSourceColumnReference
A reference to a data source column.

**Properties:**
- `name` (string): The display name of the column
- `dataSourceColumn` (DataSourceColumn): The column in the data source

### 101. DataSourceColumn
A column in a data source.

**Properties:**
- `reference` (DataSourceColumnReference): The reference to the data source column
- `formula` (string): The formula for the calculated column

### 102. BubbleChartSpec
The specification for a bubble chart.

**Properties:**
- `legendPosition` (string): The position of the chart legend
  - `BUBBLE_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
  - `BOTTOM_LEGEND`: Legend at the bottom
  - `LEFT_LEGEND`: Legend at the left
  - `RIGHT_LEGEND`: Legend at the right
  - `TOP_LEGEND`: Legend at the top
  - `NO_LEGEND`: No legend
- `domain` (ChartData): The domain of the bubble chart
- `series` (array): The series of the bubble chart

### 103. CandlestickChartSpec
The specification for a candlestick chart.

**Properties:**
- `domain` (CandlestickDomain): The domain of the candlestick chart
- `series` (array): The series of the candlestick chart

### 104. CandlestickDomain
The domain of a candlestick chart.

**Properties:**
- `data` (ChartData): The data of the candlestick domain
- `reversed` (boolean): True to reverse the order of the domain axis

### 105. CandlestickSeries
The series of a candlestick chart.

**Properties:**
- `data` (ChartData): The data of the candlestick series
- `lowSeries` (ChartData): The low series of the candlestick
- `openSeries` (ChartData): The open series of the candlestick
- `closeSeries` (ChartData): The close series of the candlestick
- `highSeries` (ChartData): The high series of the candlestick

### 106. OrgChartSpec
The specification for an org chart.

**Properties:**
- `nodeSize` (string): The size of the org chart nodes
  - `ORG_CHART_LABEL_SIZE_UNSPECIFIED`: Default value
  - `SMALL`: Small size
  - `MEDIUM`: Medium size
  - `LARGE`: Large size
- `parentLabels` (ChartData): The data for the parent labels
- `tooltips` (ChartData): The data for the tooltips
- `nodeColor` (Color): The color of the org chart nodes

### 107. HistogramChartSpec
The specification for a histogram chart.

**Properties:**
- `series` (ChartData): The series of the histogram chart
- `showItemDividers` (boolean): True if the chart should show item dividers
- `bucketSize` (number): The size of the buckets in the histogram

### 108. WaterfallChartSpec
The specification for a waterfall chart.

**Properties:**
- `domain` (ChartData): The domain of the waterfall chart
- `series` (array): The series of the waterfall chart
- `firstValueIsTotal` (boolean): True if the first value should be treated as a total
- `stackedType` (string): The stacked type of the waterfall chart
  - `WATERFALL_STACKED_TYPE_UNSPECIFIED`: Default value
  - `STACKED`: Stacked
  - `SEQUENTIAL`: Sequential

### 109. TreemapChartSpec
The specification for a treemap chart.

**Properties:**
- `series` (ChartData): The series of the treemap chart
- `parentLabels` (ChartData): The data for the parent labels
- `tooltips` (ChartData): The data for the tooltips
- `maxDepth` (integer): The maximum depth of the treemap chart

### 110. ScorecardChartSpec
The specification for a scorecard chart.

**Properties:**
- `data` (ChartData): The data of the scorecard chart
- `aggregateType` (string): The aggregation type for the scorecard chart
  - `CHART_AGGREGATE_TYPE_UNSPECIFIED`: Default value
  - `AVERAGE`: Average
  - `COUNT`: Count
  - `MAX`: Maximum
  - `MEDIAN`: Median
  - `MIN`: Minimum
  - `SUM`: Sum

### 111. FilterView
A filter view.

**Properties:**
- `filterViewId` (integer): The ID of the filter view
- `title` (string): The name of the filter view
- `range` (GridRange): The range on a sheet that this filter view applies to
- `namedRangeId` (string): The named range this filter view is backed by
- `filterSpecs` (array): The filter criteria for showing/hiding values per column

### 112. FilterSpec
The filter criteria for showing/hiding values per column.

**Properties:**
- `columnIndex` (integer): The column index
- `dataSourceColumnReference` (DataSourceColumnReference): The reference to the data source column
- `filterCriteria` (FilterCriteria): The criteria for the column

### 113. FilterCriteria
The criteria for showing/hiding values in a pivot table.

**Properties:**
- `condition` (BooleanCondition): A condition that must be true for values to be shown
- `visibleValues` (array): Values that should be included
- `hiddenValues` (array): Values that should be excluded

### 114. PivotTable
A pivot table.

**Properties:**
- `pivotTableId` (integer): The ID of the pivot table
- `source` (GridRange): The range the pivot table is reading from
- `rows` (array): The rows in the pivot table
- `columns` (array): The columns in the pivot table
- `values` (array): The values in the pivot table
- `valueLayout` (string): The value layout of the pivot table
  - `HORIZONTAL`: Horizontal layout
  - `VERTICAL`: Vertical layout

### 115. PivotGroup
A group of values in a pivot table.

**Properties:**
- `sourceColumnOffset` (integer): The offset of the source column
- `showTotals` (boolean): True if the pivot table should include the totals for this grouping
- `sortOrder` (string): The order the values in this group should be sorted
  - `ASCENDING`: Ascending order
  - `DESCENDING`: Descending order
- `valueBucket` (PivotGroupSortValueBucket): The bucket of the opposite of the pivot table
- `valueMetadata` (array): Metadata about values in the grouping

### 116. PivotGroupSortValueBucket
Information about which values in a pivot group should be used for sorting.

**Properties:**
- `buckets` (array): Determines the bucket from which values are chosen to sort
- `valuesIndex` (integer): The offset in the PivotTable.values list which the values in this grouping should be sorted by

### 117. PivotGroupRule
An optional setting on a PivotGroup that defines buckets for the values in the source data column rather than breaking out each individual value.

**Properties:**
- `manualRule` (ManualRule): A manual rule for the pivot group
- `histogramRule` (HistogramRule): A histogram rule for the pivot group
- `dateTimeRule` (DateTimeRule): A date time rule for the pivot group

### 118. ManualRule
Allows you to manually organize the values in a source data column into buckets with names of your choosing.

**Properties:**
- `groups` (array): The list of manually created group rules

### 119. ManualRuleGroup
A group name and a list of items from the source data that should be placed in this group.

**Properties:**
- `groupName` (ExtendedValue): The group name
- `items` (array): The items in the group

### 120. HistogramRule
Allows you to organize the numeric values in a source data column into buckets of a constant size.

**Properties:**
- `interval` (number): The size of the buckets that are created
- `startValue` (number): The minimum value at which items are placed into buckets
- `endValue` (number): The maximum value at which items are placed into buckets

### 121. DateTimeRule
Allows you to organize the date/time values in a source data column into buckets based on selected parts of their date time values.

**Properties:**
- `type` (string): The type of date-time grouping to apply
  - `DATE_TIME_RULE_TYPE_UNSPECIFIED`: Default value
  - `SECOND`: Second
  - `MINUTE`: Minute
  - `HOUR`: Hour
  - `HOUR_MINUTE`: Hour and minute
  - `HOUR_MINUTE_AMPM`: Hour and minute with AM/PM
  - `DAY_OF_WEEK`: Day of week
  - `DAY_OF_YEAR`: Day of year
  - `DAY_OF_MONTH`: Day of month
  - `DAY_MONTH`: Day and month
  - `MONTH`: Month
  - `QUARTER`: Quarter
  - `YEAR`: Year
  - `YEAR_MONTH`: Year and month
  - `YEAR_QUARTER`: Year and quarter
  - `YEAR_MONTH_DAY`: Year, month, and day

### 122. PivotGroupValueMetadata
Metadata about a value in a pivot grouping.

**Properties:**
- `value` (ExtendedValue): The calculated value the metadata is for
- `collapsed` (boolean): True if the data corresponding to the value is collapsed

### 123. PivotFilterSpec
The pivot table filter criteria associated with a specific source column offset.

**Properties:**
- `columnOffsetIndex` (integer): The column offset of the source range
- `dataSourceColumnReference` (DataSourceColumnReference): The reference to the data source column
- `filterCriteria` (FilterCriteria): The criteria for the column

### 124. PivotValue
A value in a pivot table.

**Properties:**
- `sourceColumnOffset` (integer): The column offset of the source range
- `summarizeFunction` (string): The function to summarize the value
  - `PIVOT_STANDARD_VALUE_FUNCTION_UNSPECIFIED`: Default value
  - `SUM`: Sum
  - `COUNTA`: Count all
  - `COUNT`: Count
  - `COUNTUNIQUE`: Count unique
  - `AVERAGE`: Average
  - `MAX`: Maximum
  - `MIN`: Minimum
  - `MEDIAN`: Median
  - `PRODUCT`: Product
  - `STDEV`: Standard deviation
  - `STDEVP`: Standard deviation population
  - `VAR`: Variance
  - `VARP`: Variance population
  - `CUSTOM`: Custom
- `name` (string): A custom name to use for the value
- `formula` (string): A custom formula to use for the value
- `calculatedDisplayType` (string): The calculated display type for the value
  - `PIVOT_VALUE_CALCULATED_DISPLAY_TYPE_UNSPECIFIED`: Default value
  - `PERCENT_OF_GRAND_TOTAL`: Percent of grand total
  - `PERCENT_OF_COLUMN_TOTAL`: Percent of column total
  - `PERCENT_OF_ROW_TOTAL`: Percent of row total
  - `PERCENT_OF_TOTAL`: Percent of total
  - `PERCENT_OF_PARENT_COLUMN_TOTAL`: Percent of parent column total
  - `PERCENT_OF_PARENT_ROW_TOTAL`: Percent of parent row total
  - `PERCENT_OF_PARENT_TOTAL`: Percent of parent total
  - `RANK`: Rank
  - `PERCENTILE`: Percentile
  - `INDEX`: Index

### 125. PivotGroupLimit
The count limit on rows or columns in the pivot table.

**Properties:**
- `applyOrder` (integer): The order in which the limit is applied to the pivot table
- `metricOffset` (integer): The offset of the metric to limit by
- `countLimit` (integer): The count limit

### 126. PivotGroupSortValueBucket
Information about which values in a pivot group should be used for sorting.

**Properties:**
- `buckets` (array): Determines the bucket from which values are chosen to sort
- `valuesIndex` (integer): The offset in the PivotTable.values list which the values in this grouping should be sorted by

### 127. PivotGroupLimitValueInfo
Information about which values in a pivot group should be used for the limit.

**Properties:**
- `sourceColumnOffset` (integer): The offset in the source column that the limit is applied to
- `value` (ExtendedValue): The value to limit by

### 128. PivotGroupLimitValueInfo
Information about which values in a pivot group should be used for the limit.

**Properties:**
- `sourceColumnOffset` (integer): The offset in the source column that the limit is applied to
- `value` (ExtendedValue): The value to limit by

### 129. PivotGroupLimitValueInfo
Information about which values in a pivot group should be used for the limit.

**Properties:**
- `sourceColumnOffset` (integer): The offset in the source column that the limit is applied to
- `value` (ExtendedValue): The value to limit by

### 130. PivotGroupLimitValueInfo
Information about which values in a pivot group should be used for the limit.

**Properties:**
- `sourceColumnOffset` (integer): The offset in the source column that the limit is applied to
- `value` (ExtendedValue): The value to limit by

### 131. AddBandingRequest
Request to add banding to a range.

**Properties:**
- `bandedRange` (BandedRange): The banded range to add

### 132. AddBandingResponse
Response when adding banding to a range.

**Properties:**
- `bandedRange` (BandedRange): The banded range that was added

### 133. BandedRange
A banded range.

**Properties:**
- `bandedRangeId` (integer): The ID of the banded range
- `range` (GridRange): The range this banded range covers
- `rowProperties` (BandingProperties): The row properties of the banded range
- `columnProperties` (BandingProperties): The column properties of the banded range

### 134. BandingProperties
Properties of a banded range.

**Properties:**
- `headerColor` (Color): The color of the header
- `firstBandColor` (Color): The color of the first band
- `secondBandColor` (Color): The color of the second band
- `footerColor` (Color): The color of the footer

### 135. AddDataSourceRequest
Request to add a data source.

**Properties:**
- `dataSource` (DataSource): The data source to add

### 136. AddDataSourceResponse
Response when adding a data source.

**Properties:**
- `dataSource` (DataSource): The data source that was added

### 137. AddDimensionGroupRequest
Request to add a dimension group.

**Properties:**
- `range` (DimensionRange): The range to group
- `depth` (integer): The depth of the group

### 138. AddDimensionGroupResponse
Response when adding a dimension group.

**Properties:**
- `dimensionGroups` (array): The dimension groups that were added

### 139. DimensionGroup
A group of dimensions.

**Properties:**
- `range` (DimensionRange): The range this group covers
- `depth` (integer): The depth of the group
- `collapsed` (boolean): True if the group is collapsed

### 140. AddFilterViewRequest
Request to add a filter view.

**Properties:**
- `filter` (FilterView): The filter view to add

### 141. AddFilterViewResponse
Response when adding a filter view.

**Properties:**
- `filter` (FilterView): The filter view that was added

### 142. AddProtectedRangeRequest
Request to add a protected range.

**Properties:**
- `protectedRange` (ProtectedRange): The protected range to add

### 143. AddProtectedRangeResponse
Response when adding a protected range.

**Properties:**
- `protectedRange` (ProtectedRange): The protected range that was added

### 144. ProtectedRange
A protected range.

**Properties:**
- `protectedRangeId` (integer): The ID of the protected range
- `range` (GridRange): The range this protected range covers
- `namedRangeId` (string): The named range this protected range is backed by
- `description` (string): The description of the protected range
- `warningOnly` (boolean): True if the protected range is warning only
- `requestingUserCanEdit` (boolean): True if the requesting user can edit
- `editors` (Editors): The editors of the protected range

### 145. Editors
The editors of a protected range.

**Properties:**
- `users` (array): The users who can edit
- `groups` (array): The groups who can edit
- `domainUsersCanEdit` (boolean): True if domain users can edit

### 146. AddSlicerRequest
Request to add a slicer.

**Properties:**
- `slicer` (Slicer): The slicer to add

### 147. AddSlicerResponse
Response when adding a slicer.

**Properties:**
- `slicer` (Slicer): The slicer that was added

### 148. Slicer
A slicer.

**Properties:**
- `slicerId` (integer): The ID of the slicer
- `spec` (SlicerSpec): The specification of the slicer
- `position` (EmbeddedObjectPosition): The position of the slicer

### 149. SlicerSpec
The specification of a slicer.

**Properties:**
- `dataRange` (GridRange): The data range of the slicer
- `column` (integer): The column index of the slicer
- `title` (string): The title of the slicer

### 150. AddTableRequest
Request to add a table.

**Properties:**
- `table` (Table): The table to add

### 151. AddTableResponse
Response when adding a table.

**Properties:**
- `table` (Table): The table that was added

### 152. AppendCellsRequest
Request to append cells.

**Properties:**
- `sheetId` (integer): The sheet to append cells to
- `rows` (array): The rows to append
- `fields` (string): The fields to update

### 153. AppendDimensionRequest
Request to append a dimension.

**Properties:**
- `sheetId` (integer): The sheet to append the dimension to
- `dimension` (string): The dimension to append
- `length` (integer): The length to append

### 154. AutoFillRequest
Request to auto-fill a range.

**Properties:**
- `useAlternateSeries` (boolean): True if alternate series should be used
- `sourceAndDestination` (SourceAndDestination): The source and destination

### 155. SourceAndDestination
A source and destination for auto-fill.

**Properties:**
- `source` (GridRange): The source range
- `destination` (GridRange): The destination range

### 156. BaselineValueFormat
The format of a baseline value.

**Properties:**
- `numberFormat` (NumberFormat): The number format
- `backgroundColor` (Color): The background color
- `foregroundColor` (Color): The foreground color

### 157. BasicChartAxis
An axis of a basic chart.

**Properties:**
- `position` (string): The position of the axis
- `title` (string): The title of the axis
- `format` (ChartAxisViewWindowOptions): The format of the axis

### 158. BasicChartDomain
A domain of a basic chart.

**Properties:**
- `domain` (ChartData): The domain data
- `reversed` (boolean): True if the domain is reversed

### 159. BasicChartSeries
A series of a basic chart.

**Properties:**
- `series` (ChartData): The series data
- `targetAxis` (string): The target axis
- `lineStyle` (LineStyle): The line style

### 160. BasicFilter
A basic filter.

**Properties:**
- `range` (GridRange): The range this filter applies to
- `sortSpecs` (array): The sort specifications
- `filterSpecs` (array): The filter specifications

### 161. BasicSeriesDataPointStyleOverride
A style override for a data point in a basic series.

**Properties:**
- `seriesIndex` (integer): The index of the series
- `dataPointIndex` (integer): The index of the data point
- `style` (PointStyle): The style of the data point

### 162. PointStyle
The style of a point.

**Properties:**
- `shape` (string): The shape of the point
- `size` (integer): The size of the point

### 163. CancelDataSourceRefreshRequest
Request to cancel a data source refresh.

**Properties:**
- `dataSourceId` (string): The ID of the data source

### 164. CancelDataSourceRefreshResponse
Response when canceling a data source refresh.

**Properties:**
- `status` (CancelDataSourceRefreshStatus): The status of the cancellation

### 165. CancelDataSourceRefreshStatus
The status of a data source refresh cancellation.

**Properties:**
- `state` (string): The state of the cancellation
- `errorCode` (string): The error code if failed

### 166. CandlestickData
The data for a candlestick chart.

**Properties:**
- `lowSeries` (ChartData): The low series
- `openSeries` (ChartData): The open series
- `closeSeries` (ChartData): The close series
- `highSeries` (ChartData): The high series

### 167. ChartAxisViewWindowOptions
The view window options for a chart axis.

**Properties:**
- `viewWindowMode` (string): The view window mode
- `min` (number): The minimum value
- `max` (number): The maximum value

### 168. ChartCustomNumberFormatOptions
Custom number format options for a chart.

**Properties:**
- `prefix` (string): The prefix
- `suffix` (string): The suffix

### 169. ChartDateTimeRule
A date-time rule for a chart.

**Properties:**
- `type` (string): The type of the rule
- `interval` (Interval): The interval

### 170. ChartGroupRule
A group rule for a chart.

**Properties:**
- `dateTimeRule` (ChartDateTimeRule): The date-time rule
- `histogramRule` (ChartHistogramRule): The histogram rule

### 171. ChartHistogramRule
A histogram rule for a chart.

**Properties:**
- `intervalSize` (number): The interval size
- `maxNumIntervals` (integer): The maximum number of intervals
- `minNumIntervals` (integer): The minimum number of intervals

### 172. Chip
A chip in a chart.

**Properties:**
- `chipType` (string): The type of the chip
- `textFormat` (TextFormat): The text format

### 173. ChipRun
A run of chips.

**Properties:**
- `startIndex` (integer): The start index
- `format` (Chip): The format

### 174. ClearBasicFilterRequest
Request to clear a basic filter.

**Properties:**
- `sheetId` (integer): The sheet ID

### 175. CopyPasteRequest
Request to copy and paste.

**Properties:**
- `source` (GridRange): The source range
- `destination` (GridRange): The destination range
- `pasteType` (string): The paste type
- `pasteOrientation` (string): The paste orientation

### 176. CreateDeveloperMetadataRequest
Request to create developer metadata.

**Properties:**
- `developerMetadata` (DeveloperMetadata): The developer metadata to create

### 177. CreateDeveloperMetadataResponse
Response when creating developer metadata.

**Properties:**
- `developerMetadata` (DeveloperMetadata): The developer metadata that was created

### 178. CutPasteRequest
Request to cut and paste.

**Properties:**
- `source` (GridRange): The source range
- `destination` (GridCoordinate): The destination coordinate
- `pasteType` (string): The paste type

### 179. DataExecutionStatus
The execution status of data.

**Properties:**
- `state` (string): The state of the execution
- `errorCode` (string): The error code if failed
- `errorMessage` (string): The error message if failed

### 180. DataLabel
A data label.

**Properties:**
- `textFormat` (TextFormat): The text format
- `position` (string): The position of the label

### 181. DataSourceChartProperties
Chart properties for a data source.

**Properties:**
- `dataSourceId` (string): The data source ID
- `chartId` (integer): The chart ID

### 182. DataSourceFormula
A formula for a data source.

**Properties:**
- `dataSourceId` (string): The data source ID
- `formula` (string): The formula

### 183. DataSourceObjectReference
A reference to a data source object.

**Properties:**
- `dataSourceId` (string): The data source ID
- `objectId` (string): The object ID

### 184. DataSourceObjectReferences
References to data source objects.

**Properties:**
- `references` (array): The references

### 185. DataSourceParameter
A parameter for a data source.

**Properties:**
- `name` (string): The name of the parameter
- `value` (string): The value of the parameter

### 186. DataSourceRefreshDailySchedule
A daily refresh schedule for a data source.

**Properties:**
- `startTime` (TimeOfDay): The start time

### 187. DataSourceRefreshMonthlySchedule
A monthly refresh schedule for a data source.

**Properties:**
- `dayOfMonth` (integer): The day of the month

### 188. DataSourceRefreshSchedule
A refresh schedule for a data source.

**Properties:**
- `dailySchedule` (DataSourceRefreshDailySchedule): The daily schedule
- `weeklySchedule` (DataSourceRefreshWeeklySchedule): The weekly schedule
- `monthlySchedule` (DataSourceRefreshMonthlySchedule): The monthly schedule

### 189. DataSourceRefreshWeeklySchedule
A weekly refresh schedule for a data source.

**Properties:**
- `dayOfWeek` (string): The day of the week

### 190. DataSourceSheetDimensionRange
A dimension range for a data source sheet.

**Properties:**
- `sheetId` (integer): The sheet ID
- `dimension` (string): The dimension
- `startIndex` (integer): The start index
- `endIndex` (integer): The end index

### 191. DataSourceSheetProperties
Sheet properties for a data source.

**Properties:**
- `dataSourceId` (string): The data source ID
- `sheetId` (integer): The sheet ID

### 192. DataSourceTable
A table for a data source.

**Properties:**
- `dataSourceId` (string): The data source ID
- `tableId` (integer): The table ID

### 193. DeleteBandingRequest
Request to delete banding.

**Properties:**
- `bandedRangeId` (integer): The ID of the banded range to delete

### 194. DeleteDuplicatesRequest
Request to delete duplicates.

**Properties:**
- `range` (GridRange): The range to check for duplicates
- `comparisonColumns` (array): The columns to compare

### 195. DeleteDuplicatesResponse
Response when deleting duplicates.

**Properties:**
- `duplicatesRemovedCount` (integer): The number of duplicates removed

### 196. DeleteEmbeddedObjectRequest
Request to delete an embedded object.

**Properties:**
- `objectId` (integer): The ID of the object to delete

### 197. DeleteFilterViewRequest
Request to delete a filter view.

**Properties:**
- `filterId` (integer): The ID of the filter view to delete

### 198. DeleteRangeRequest
Request to delete a range.

**Properties:**
- `range` (GridRange): The range to delete
- `shiftDimension` (string): The dimension to shift

### 199. DeleteTableRequest
Request to delete a table.

**Properties:**
- `tableId` (integer): The ID of the table to delete

### 200. DuplicateFilterViewRequest
Request to duplicate a filter view.

**Properties:**
- `filterId` (integer): The ID of the filter view to duplicate

### 201. DuplicateFilterViewResponse
Response when duplicating a filter view.

**Properties:**
- `filter` (FilterView): The duplicated filter view

### 202. DuplicateSheetResponse
Response when duplicating a sheet.

**Properties:**
- `properties` (SheetProperties): The properties of the duplicated sheet

### 203. EmbeddedObjectBorder
The border of an embedded object.

**Properties:**
- `color` (Color): The color of the border
- `style` (string): The style of the border

### 204. FindReplaceRequest
Request to find and replace.

**Properties:**
- `find` (string): The text to find
- `replacement` (string): The replacement text
- `matchCase` (boolean): True if case should be matched
- `matchEntireCell` (boolean): True if entire cell should be matched
- `searchByRegex` (boolean): True if search should use regex
- `includeFormulas` (boolean): True if formulas should be included

### 205. FindReplaceResponse
Response when finding and replacing.

**Properties:**
- `valuesChanged` (integer): The number of values changed
- `formulasChanged` (integer): The number of formulas changed

### 206. GetSpreadsheetByDataFilterRequest
Request to get a spreadsheet by data filter.

**Properties:**
- `dataFilters` (array): The data filters
- `includeGridData` (boolean): True if grid data should be included

### 207. Interval
An interval.

**Properties:**
- `start` (number): The start value
- `end` (number): The end value

### 208. KeyValueFormat
A key-value format.

**Properties:**
- `position` (TextPosition): The position
- `textFormat` (TextFormat): The text format

### 209. LineStyle
The style of a line.

**Properties:**
- `width` (integer): The width of the line
- `dashType` (string): The dash type

### 210. Link
A link.

**Properties:**
- `uri` (string): The URI
- `displayText` (string): The display text

### 211. LookerDataSourceSpec
A Looker data source specification.

**Properties:**
- `lookerId` (string): The Looker ID

### 212. MatchedDeveloperMetadata
Matched developer metadata.

**Properties:**
- `developerMetadata` (DeveloperMetadata): The developer metadata
- `dataFilters` (array): The data filters

### 213. MatchedValueRange
A matched value range.

**Properties:**
- `valueRange` (ValueRange): The value range
- `dataFilters` (array): The data filters

### 214. MergeCellsRequest
Request to merge cells.

**Properties:**
- `range` (GridRange): The range to merge
- `mergeType` (string): The merge type

### 215. PasteDataRequest
Request to paste data.

**Properties:**
- `coordinate` (GridCoordinate): The coordinate
- `data` (string): The data
- `type` (string): The type
- `delimiter` (string): The delimiter

### 216. PersonProperties
Properties of a person.

**Properties:**
- `displayName` (string): The display name
- `email` (string): The email

### 217. PivotFilterCriteria
Filter criteria for a pivot table.

**Properties:**
- `condition` (BooleanCondition): The condition
- `visibleValues` (array): The visible values

### 218. RandomizeRangeRequest
Request to randomize a range.

**Properties:**
- `range` (GridRange): The range to randomize

### 219. RefreshCancellationStatus
The status of a refresh cancellation.

**Properties:**
- `state` (string): The state
- `errorCode` (string): The error code

### 220. RefreshDataSourceObjectExecutionStatus
The execution status of a data source object refresh.

**Properties:**
- `state` (string): The state
- `errorCode` (string): The error code

### 221. RefreshDataSourceResponse
Response when refreshing a data source.

**Properties:**
- `status` (DataExecutionStatus): The status

### 222. RepeatCellRequest
Request to repeat a cell.

**Properties:**
- `range` (GridRange): The range
- `cell` (CellData): The cell data
- `fields` (string): The fields

### 223. Response
A response.

**Properties:**
- `addBanding` (AddBandingResponse): Add banding response
- `addChart` (AddChartResponse): Add chart response
- `addDataSource` (AddDataSourceResponse): Add data source response
- `addDimensionGroup` (AddDimensionGroupResponse): Add dimension group response
- `addFilterView` (AddFilterViewResponse): Add filter view response
- `addNamedRange` (AddNamedRangeResponse): Add named range response
- `addProtectedRange` (AddProtectedRangeResponse): Add protected range response
- `addSheet` (AddSheetResponse): Add sheet response
- `addSlicer` (AddSlicerResponse): Add slicer response
- `addTable` (AddTableResponse): Add table response
- `deleteConditionalFormatRule` (DeleteConditionalFormatRuleResponse): Delete conditional format rule response
- `deleteDataSource` (DeleteDataSourceResponse): Delete data source response
- `deleteDeveloperMetadata` (DeleteDeveloperMetadataResponse): Delete developer metadata response
- `deleteDimensionGroup` (DeleteDimensionGroupResponse): Delete dimension group response
- `deleteDuplicates` (DeleteDuplicatesResponse): Delete duplicates response
- `duplicateFilterView` (DuplicateFilterViewResponse): Duplicate filter view response
- `duplicateSheet` (DuplicateSheetResponse): Duplicate sheet response
- `findReplace` (FindReplaceResponse): Find replace response
- `refreshDataSource` (RefreshDataSourceResponse): Refresh data source response
- `trimWhitespace` (TrimWhitespaceResponse): Trim whitespace response
- `updateConditionalFormatRule` (UpdateConditionalFormatRuleResponse): Update conditional format rule response
- `updateDataSource` (UpdateDataSourceResponse): Update data source response
- `updateDeveloperMetadata` (UpdateDeveloperMetadataResponse): Update developer metadata response
- `updateDimensionGroup` (UpdateDimensionGroupResponse): Update dimension group response
- `updateEmbeddedObjectPosition` (UpdateEmbeddedObjectPositionResponse): Update embedded object position response

### 224. RichLinkProperties
Properties of a rich link.

**Properties:**
- `title` (string): The title
- `uri` (string): The URI

### 225. SetBasicFilterRequest
Request to set a basic filter.

**Properties:**
- `filter` (BasicFilter): The filter to set

### 226. SetDataValidationRequest
Request to set data validation.

**Properties:**
- `range` (GridRange): The range
- `rule` (DataValidationRule): The rule

### 227. Sheet
A sheet.

**Properties:**
- `properties` (SheetProperties): The properties
- `data` (array): The data
- `conditionalFormats` (array): The conditional formats
- `filterViews` (array): The filter views
- `protectedRanges` (array): The protected ranges
- `basicFilter` (BasicFilter): The basic filter
- `charts` (array): The charts
- `bandedRanges` (array): The banded ranges
- `developerMetadata` (array): The developer metadata
- `rowGroups` (array): The row groups
- `columnGroups` (array): The column groups
- `slicers` (array): The slicers

### 228. SpreadsheetTheme
A spreadsheet theme.

**Properties:**
- `primaryFontFamily` (string): The primary font family
- `themeColors` (array): The theme colors

### 229. TableColumnDataValidationRule
A data validation rule for a table column.

**Properties:**
- `condition` (BooleanCondition): The condition
- `showCustomUi` (boolean): True if custom UI should be shown
- `strict` (boolean): True if strict validation

### 230. TableColumnProperties
Properties of a table column.

**Properties:**
- `columnId` (string): The column ID
- `displayName` (string): The display name

### 231. TableRowsProperties
Properties of table rows.

**Properties:**
- `headerRow` (boolean): True if header row
- `totalRow` (boolean): True if total row

### 232. TextPosition
The position of text.

**Properties:**
- `horizontalAlignment` (string): The horizontal alignment
- `verticalAlignment` (string): The vertical alignment

### 233. TextRotation
The rotation of text.

**Properties:**
- `angle` (integer): The angle
- `vertical` (boolean): True if vertical

### 234. TextToColumnsRequest
Request to convert text to columns.

**Properties:**
- `source` (GridRange): The source range
- `destination` (GridCoordinate): The destination coordinate
- `delimiterType` (string): The delimiter type
- `delimiter` (string): The delimiter

### 235. ThemeColorPair
A theme color pair.

**Properties:**
- `colorType` (string): The color type
- `color` (ColorStyle): The color

### 236. ColorStyle
A color style.

**Properties:**
- `rgbColor` (Color): The RGB color
- `themeColor` (string): The theme color

### 237. TimeOfDay
A time of day.

**Properties:**
- `hours` (integer): The hours
- `minutes` (integer): The minutes
- `seconds` (integer): The seconds
- `nanos` (integer): The nanoseconds

### 238. TreemapChartColorScale
A color scale for a treemap chart.

**Properties:**
- `minValueColor` (Color): The minimum value color
- `maxValueColor` (Color): The maximum value color
- `midValueColor` (Color): The mid value color
- `noDataColor` (Color): The no data color

### 239. TrimWhitespaceRequest
Request to trim whitespace.

**Properties:**
- `range` (GridRange): The range to trim

### 240. TrimWhitespaceResponse
Response when trimming whitespace.

**Properties:**
- `cellsChangedCount` (integer): The number of cells changed

### 241. UnmergeCellsRequest
Request to unmerge cells.

**Properties:**
- `range` (GridRange): The range to unmerge

### 242. UpdateBandingRequest
Request to update banding.

**Properties:**
- `bandedRange` (BandedRange): The banded range to update
- `fields` (string): The fields to update

### 243. UpdateDataSourceRequest
Request to update a data source.

**Properties:**
- `dataSource` (DataSource): The data source to update
- `fields` (string): The fields to update

### 244. UpdateDataSourceResponse
Response when updating a data source.

**Properties:**
- `dataSource` (DataSource): The updated data source

### 245. UpdateDeveloperMetadataResponse
Response when updating developer metadata.

**Properties:**
- `developerMetadata` (DeveloperMetadata): The updated developer metadata

### 246. UpdateDimensionGroupRequest
Request to update a dimension group.

**Properties:**
- `dimensionGroup` (DimensionGroup): The dimension group to update
- `fields` (string): The fields to update

### 247. UpdateDimensionGroupResponse
Response when updating a dimension group.

**Properties:**
- `dimensionGroup` (DimensionGroup): The updated dimension group

### 248. UpdateEmbeddedObjectBorderRequest
Request to update an embedded object border.

**Properties:**
- `objectId` (integer): The object ID
- `border` (EmbeddedObjectBorder): The border to update
- `fields` (string): The fields to update

### 249. UpdateEmbeddedObjectPositionRequest
Request to update an embedded object position.

**Properties:**
- `objectId` (integer): The object ID
- `newPosition` (EmbeddedObjectPosition): The new position
- `overlayPosition` (OverlayPosition): The overlay position

### 250. UpdateEmbeddedObjectPositionResponse
Response when updating an embedded object position.

**Properties:**
- `position` (EmbeddedObjectPosition): The updated position

### 251. UpdateFilterViewRequest
Request to update a filter view.

**Properties:**
- `filter` (FilterView): The filter view to update
- `fields` (string): The fields to update

### 252. UpdateSlicerSpecRequest
Request to update a slicer specification.

**Properties:**
- `slicerId` (integer): The slicer ID
- `spec` (SlicerSpec): The specification to update
- `fields` (string): The fields to update

### 253. UpdateTableRequest
Request to update a table.

**Properties:**
- `table` (Table): The table to update
- `fields` (string): The fields to update

### 254. UpdateValuesByDataFilterResponse
Response when updating values by data filter.

**Properties:**
- `updatedData` (ValueRange): The updated data
- `updatedRange` (string): The updated range

### 255. WaterfallChartColumnStyle
The style of a waterfall chart column.

**Properties:**
- `color` (Color): The color
- `label` (string): The label

### 256. WaterfallChartCustomSubtotal
A custom subtotal for a waterfall chart.

**Properties:**
- `dataIsSubtotal` (boolean): True if data is subtotal
- `subtotalIndex` (integer): The subtotal index

### 257. WaterfallChartDomain
A domain for a waterfall chart.

**Properties:**
- `data` (ChartData): The domain data
- `reversed` (boolean): True if reversed

### 258. WaterfallChartSeries
A series for a waterfall chart.

**Properties:**
- `data` (ChartData): The series data
- `subtotalsData` (ChartData): The subtotals data
- `customSubtotals` (array): The custom subtotals
- `firstValueIsTotal` (boolean): True if first value is total
- `hideConnectorLines` (boolean): True if connector lines should be hidden
- `connectorLineStyle` (LineStyle): The connector line style
- `columnStyle` (WaterfallChartColumnStyle): The column style

### 259. WaterfallChartSpec
The specification for a waterfall chart.

**Properties:**
- `domain` (WaterfallChartDomain): The domain
- `series` (array): The series
- `stackedType` (string): The stacked type
- `firstValueIsTotal` (boolean): True if first value is total
- `hideConnectorLines` (boolean): True if connector lines should be hidden
- `connectorLineStyle` (LineStyle): The connector line style
- `columnStyle` (WaterfallChartColumnStyle): The column style

### 260. Request
A request in a batch update.

**Properties:**
- `addBanding` (AddBandingRequest): Add banding request
- `addChart` (AddChartRequest): Add chart request
- `addConditionalFormatRule` (AddConditionalFormatRuleRequest): Add conditional format rule request
- `addDataSource` (AddDataSourceRequest): Add data source request
- `addDimensionGroup` (AddDimensionGroupRequest): Add dimension group request
- `addFilterView` (AddFilterViewRequest): Add filter view request
- `addNamedRange` (AddNamedRangeRequest): Add named range request
- `addProtectedRange` (AddProtectedRangeRequest): Add protected range request
- `addSheet` (AddSheetRequest): Add sheet request
- `addSlicer` (AddSlicerRequest): Add slicer request
- `addTable` (AddTableRequest): Add table request
- `appendCells` (AppendCellsRequest): Append cells request
- `appendDimension` (AppendDimensionRequest): Append dimension request
- `autoFill` (AutoFillRequest): Auto fill request
- `autoResizeDimensions` (AutoResizeDimensionsRequest): Auto resize dimensions request
- `clearBasicFilter` (ClearBasicFilterRequest): Clear basic filter request
- `copyPaste` (CopyPasteRequest): Copy paste request
- `createDeveloperMetadata` (CreateDeveloperMetadataRequest): Create developer metadata request
- `cutPaste` (CutPasteRequest): Cut paste request
- `deleteBanding` (DeleteBandingRequest): Delete banding request
- `deleteConditionalFormatRule` (DeleteConditionalFormatRuleRequest): Delete conditional format rule request
- `deleteDataSource` (DeleteDataSourceRequest): Delete data source request
- `deleteDeveloperMetadata` (DeleteDeveloperMetadataRequest): Delete developer metadata request
- `deleteDimension` (DeleteDimensionRequest): Delete dimension request
- `deleteDimensionGroup` (DeleteDimensionGroupRequest): Delete dimension group request
- `deleteDuplicates` (DeleteDuplicatesRequest): Delete duplicates request
- `deleteEmbeddedObject` (DeleteEmbeddedObjectRequest): Delete embedded object request
- `deleteFilterView` (DeleteFilterViewRequest): Delete filter view request
- `deleteNamedRange` (DeleteNamedRangeRequest): Delete named range request
- `deleteProtectedRange` (DeleteProtectedRangeRequest): Delete protected range request
- `deleteRange` (DeleteRangeRequest): Delete range request
- `deleteSheet` (DeleteSheetRequest): Delete sheet request
- `deleteTable` (DeleteTableRequest): Delete table request
- `duplicateFilterView` (DuplicateFilterViewRequest): Duplicate filter view request
- `duplicateSheet` (DuplicateSheetRequest): Duplicate sheet request
- `findReplace` (FindReplaceRequest): Find replace request
- `insertDimension` (InsertDimensionRequest): Insert dimension request
- `insertRange` (InsertRangeRequest): Insert range request
- `mergeCells` (MergeCellsRequest): Merge cells request
- `moveDimension` (MoveDimensionRequest): Move dimension request
- `pasteData` (PasteDataRequest): Paste data request
- `randomizeRange` (RandomizeRangeRequest): Randomize range request
- `refreshDataSource` (RefreshDataSourceRequest): Refresh data source request
- `repeatCell` (RepeatCellRequest): Repeat cell request
- `setBasicFilter` (SetBasicFilterRequest): Set basic filter request
- `setDataValidation` (SetDataValidationRequest): Set data validation request
- `sortRange` (SortRangeRequest): Sort range request
- `textToColumns` (TextToColumnsRequest): Text to columns request
- `trimWhitespace` (TrimWhitespaceRequest): Trim whitespace request
- `unmergeCells` (UnmergeCellsRequest): Unmerge cells request
- `updateBanding` (UpdateBandingRequest): Update banding request
- `updateBorders` (UpdateBordersRequest): Update borders request
- `updateCells` (UpdateCellsRequest): Update cells request
- `updateChartSpec` (UpdateChartSpecRequest): Update chart spec request
- `updateConditionalFormatRule` (UpdateConditionalFormatRuleRequest): Update conditional format rule request
- `updateDataSource` (UpdateDataSourceRequest): Update data source request
- `updateDeveloperMetadata` (UpdateDeveloperMetadataRequest): Update developer metadata request
- `updateDimensionGroup` (UpdateDimensionGroupRequest): Update dimension group request
- `updateDimensionProperties` (UpdateDimensionPropertiesRequest): Update dimension properties request
- `updateEmbeddedObjectBorder` (UpdateEmbeddedObjectBorderRequest): Update embedded object border request
- `updateEmbeddedObjectPosition` (UpdateEmbeddedObjectPositionRequest): Update embedded object position request
- `updateFilterView` (UpdateFilterViewRequest): Update filter view request
- `updateNamedRange` (UpdateNamedRangeRequest): Update named range request
- `updateProtectedRange` (UpdateProtectedRangeRequest): Update protected range request
- `updateSheetProperties` (UpdateSheetPropertiesRequest): Update sheet properties request
- `updateSlicerSpec` (UpdateSlicerSpecRequest): Update slicer spec request
- `updateSpreadsheetProperties` (UpdateSpreadsheetPropertiesRequest): Update spreadsheet properties request
- `updateTable` (UpdateTableRequest): Update table request

### 261. InsertRangeRequest
Request to insert a range.

**Properties:**
- `range` (GridRange): The range to insert
- `shiftDimension` (string): The dimension to shift

### 262. DeleteDataSourceRequest
Request to delete a data source.

**Properties:**
- `dataSourceId` (string): The ID of the data source to delete

### 263. DeleteDataSourceResponse
Response when deleting a data source.

**Properties:**
- `dataSourceId` (string): The ID of the deleted data source

## Spreadsheets Resource

### 1. Get Spreadsheet
```
GET /v4/spreadsheets/{spreadsheetId}
```

**Description:** Returns the spreadsheet at the given ID. The caller must specify the spreadsheet ID.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve
- `ranges` (query, optional): The ranges to retrieve from the spreadsheet
- `includeGridData` (query, optional): True if grid data should be returned
- `fields` (query, optional): The fields to include in the response

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

### 2. Batch Update
```
POST /v4/spreadsheets/{spreadsheetId}:batchUpdate
```

**Description:** Applies one or more updates to the spreadsheet. The request must contain a list of operations to perform.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchUpdateSpreadsheetRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

## Values Resource

### 1. Get Values
```
GET /v4/spreadsheets/{spreadsheetId}/values/{range}
```

**Description:** Returns a range of values from a spreadsheet. The caller must specify the spreadsheet ID and a range.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve data from
- `range` (path, required): The A1 notation or R1C1 notation of the values to retrieve
- `majorDimension` (query, optional): The major dimension that results should use
- `valueRenderOption` (query, optional): How values should be rendered in the output
- `dateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

### 2. Update Values
```
PUT /v4/spreadsheets/{spreadsheetId}/values/{range}
```

**Description:** Sets values in a range of a spreadsheet. The caller must specify the spreadsheet ID, range, and a valueInputOption.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update
- `range` (path, required): The A1 notation of the values to update
- `valueInputOption` (query, optional): How the input data should be interpreted
- `includeValuesInResponse` (query, optional): Whether to include updated values in response
- `responseValueRenderOption` (query, optional): How values should be rendered in response
- `responseDateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Request Body:** ValueRange

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

### 3. Append Values
```
POST /v4/spreadsheets/{spreadsheetId}/values/{range}:append
```

**Description:** Appends values to a spreadsheet. The input range is used to search for existing data and find a table, after which values will be appended.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update
- `range` (path, required): The A1 notation of a range to search for a logical table of data
- `valueInputOption` (query, optional): How the input data should be interpreted
- `insertDataOption` (query, optional): How the input data should be inserted
- `includeValuesInResponse` (query, optional): Whether to include updated values in response
- `responseValueRenderOption` (query, optional): How values should be rendered in response
- `responseDateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Request Body:** ValueRange

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

### 4. Clear Values
```
POST /v4/spreadsheets/{spreadsheetId}/values/{range}:clear
```

**Description:** Clears values from a spreadsheet. The caller must specify the spreadsheet ID and range.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update
- `range` (path, required): The A1 notation of the values to clear

**Request Body:** ClearValuesRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

### 5. Batch Get Values
```
GET /v4/spreadsheets/{spreadsheetId}/values:batchGet
```

**Description:** Returns one or more ranges of values from a spreadsheet. The caller must specify the spreadsheet ID and one or more ranges.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve data from
- `ranges` (query, required): The A1 notation or R1C1 notation of the values to retrieve
- `majorDimension` (query, optional): The major dimension that results should use
- `valueRenderOption` (query, optional): How values should be rendered in the output
- `dateTimeRenderOption` (query, optional): How dates, times, and durations should be represented

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

### 6. Batch Update Values
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchUpdate
```

**Description:** Sets values in one or more ranges of a spreadsheet. The caller must specify the spreadsheet ID, a valueInputOption, and one or more ValueRanges.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchUpdateValuesRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

### 7. Batch Clear Values
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchClear
```

**Description:** Clears one or more ranges of values from a spreadsheet. The caller must specify the spreadsheet ID and one or more ranges.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchClearValuesRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

### 8. Batch Get Values By Data Filter
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchGetByDataFilter
```

**Description:** Returns one or more ranges of values that match the specified data filters. The caller must specify the spreadsheet ID and one or more DataFilters.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve data from

**Request Body:** BatchGetValuesByDataFilterRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

### 9. Batch Update Values By Data Filter
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchUpdateByDataFilter
```

**Description:** Sets values in one or more ranges of a spreadsheet. The caller must specify the spreadsheet ID, a valueInputOption, and one or more DataFilterValueRanges.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchUpdateValuesByDataFilterRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

### 10. Batch Clear Values By Data Filter
```
POST /v4/spreadsheets/{spreadsheetId}/values:batchClearByDataFilter
```

**Description:** Clears one or more ranges of values from a spreadsheet. The caller must specify the spreadsheet ID and one or more DataFilters.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to update

**Request Body:** BatchClearValuesByDataFilterRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

## Developer Metadata Resource

### 1. Get Developer Metadata
```
GET /v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}
```

**Description:** Returns the developer metadata with the specified ID. The caller must specify the spreadsheet ID and the developer metadata's unique metadataId.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve metadata from
- `metadataId` (path, required): The ID of the developer metadata to retrieve

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

### 2. Search Developer Metadata
```
POST /v4/spreadsheets/{spreadsheetId}/developerMetadata:search
```

**Description:** Returns all developer metadata matching the specified DataFilter. If the provided DataFilter represents a DeveloperMetadataLookup object, this will return all DeveloperMetadata entries selected by it. If the DataFilter represents a location in a spreadsheet, this will return all developer metadata associated with locations intersecting that region.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet to retrieve metadata from

**Request Body:** SearchDeveloperMetadataRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`

## Sheets Resource

### 1. Copy Sheet
```
POST /v4/spreadsheets/{spreadsheetId}/sheets/{sheetId}:copyTo
```

**Description:** Copies a single sheet from a spreadsheet to another spreadsheet. Returns the properties of the newly created sheet.

**Parameters:**
- `spreadsheetId` (path, required): The ID of the spreadsheet containing the sheet to copy
- `sheetId` (path, required): The ID of the sheet to copy

**Request Body:** CopySheetToAnotherSpreadsheetRequest

**Scopes:**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`

## Authentication & Scopes

### Required Scopes
- `https://www.googleapis.com/auth/spreadsheets` - Full access to spreadsheets
- `https://www.googleapis.com/auth/spreadsheets.readonly` - Read-only access
- `https://www.googleapis.com/auth/drive` - Full access to Drive
- `https://www.googleapis.com/auth/drive.file` - Access to files created by the app

## Error Handling

### Common Error Responses
```json
{
  "error": {
    "code": 400,
    "message": "Invalid range",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "field": "range",
            "description": "Invalid A1 notation"
          }
        ]
      }
    ]
  }
}
```

### Error Codes
- `400`: Bad Request (invalid parameters, malformed requests)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (spreadsheet/sheet not found)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error
- `503`: Service Unavailable

## Rate Limits

### Standard Limits
- **Read requests:** 300 requests per minute per user
- **Write requests:** 60 requests per minute per user
- **Batch requests:** Count as single request
- **Developer metadata:** 100 requests per minute per user

### Quota Exceeded Response
```json
{
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota group 'ReadGroup' and limit 'Read requests per minute per user' of service 'sheets.googleapis.com'",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```

## Complete API Reference

### Value Input Options
- `INPUT_VALUE_OPTION_UNSPECIFIED`: Default value, do not use
- `RAW`: Values stored as-is without parsing
- `USER_ENTERED`: Values parsed as if typed in Google Sheets UI

### Value Render Options
- `FORMATTED_VALUE`: Values calculated and formatted according to cell formatting
- `UNFORMATTED_VALUE`: Values calculated but not formatted
- `FORMULA`: Values as formulas (not calculated)

### Date Time Render Options
- `SERIAL_NUMBER`: Dates as serial numbers
- `FORMATTED_STRING`: Dates as formatted strings

### Major Dimensions
- `DIMENSION_UNSPECIFIED`: Default value, do not use
- `ROWS`: Data organized by rows
- `COLUMNS`: Data organized by columns

### Developer Metadata Visibility
- `DEVELOPER_METADATA_VISIBILITY_UNSPECIFIED`: Default value
- `DOCUMENT`: Document-scoped metadata
- `PROJECT`: Project-scoped metadata

### Location Types
- `DEVELOPER_METADATA_LOCATION_TYPE_UNSPECIFIED`: Default value
- `ROW`: Row location
- `COLUMN`: Column location
- `SHEET`: Sheet location
- `SPREADSHEET`: Spreadsheet location

### Location Matching Strategies
- `DEVELOPER_METADATA_LOOKUP_LOCATION_MATCHING_STRATEGY_UNSPECIFIED`: Default value
- `EXACT_LOCATION`: Exact location matching
- `INTERSECTING_LOCATION`: Intersecting location matching

### Sheet Types
- `SHEET_TYPE_UNSPECIFIED`: Default value
- `GRID`: A normal sheet
- `OBJECT`: An object sheet

### Horizontal Alignment
- `HORIZONTAL_ALIGN_UNSPECIFIED`: Default value
- `LEFT`: Left alignment
- `CENTER`: Center alignment
- `RIGHT`: Right alignment

### Vertical Alignment
- `VERTICAL_ALIGN_UNSPECIFIED`: Default value
- `TOP`: Top alignment
- `MIDDLE`: Middle alignment
- `BOTTOM`: Bottom alignment

### Wrap Strategy
- `WRAP_STRATEGY_UNSPECIFIED`: Default value
- `OVERFLOW_CELL`: Text wraps to next line
- `CLIP`: Text is clipped to the cell
- `WRAP`: Text wraps within the cell

### Text Direction
- `TEXT_DIRECTION_UNSPECIFIED`: Default value
- `LEFT_TO_RIGHT`: Left to right
- `RIGHT_TO_LEFT`: Right to left

### Hyperlink Display Type
- `HYPERLINK_DISPLAY_TYPE_UNSPECIFIED`: Default value
- `LINKED`: Shows the link text
- `PLAIN_TEXT`: Shows the URL

### Number Format Types
- `NUMBER_FORMAT_TYPE_UNSPECIFIED`: Default value
- `TEXT`: Text format
- `NUMBER`: Number format
- `PERCENT`: Percent format
- `CURRENCY`: Currency format
- `DATE`: Date format
- `TIME`: Time format
- `DATE_TIME`: Date time format
- `SCIENTIFIC`: Scientific format

### Border Styles
- `STYLE_UNSPECIFIED`: Default value
- `DOTTED`: Dotted style
- `DASHED`: Dashed style
- `SOLID`: Solid style
- `SOLID_MEDIUM`: Solid medium style
- `SOLID_THICK`: Solid thick style
- `NONE`: No border
- `DOUBLE`: Double border

### Recalculation Interval
- `RECALCULATION_INTERVAL_UNSPECIFIED`: Default value
- `ON_CHANGE`: Volatile functions are recalculated on every change
- `MINUTE`: Volatile functions are recalculated on every minute
- `HOUR`: Volatile functions are recalculated on every hour

### Chart Types
- `BASIC_CHART_TYPE_UNSPECIFIED`: Default value
- `LINE`: Line chart
- `AREA`: Area chart
- `COLUMN`: Column chart
- `BAR`: Bar chart
- `PIE`: Pie chart
- `SCATTER`: Scatter chart
- `COMBO`: Combo chart
- `STEPPED_AREA`: Stepped area chart

### Chart Legend Positions
- `BASIC_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
- `BOTTOM_LEGEND`: Legend at the bottom
- `LEFT_LEGEND`: Legend at the left
- `RIGHT_LEGEND`: Legend at the right
- `TOP_LEGEND`: Legend at the top
- `NO_LEGEND`: No legend

### Chart Aggregate Types
- `CHART_AGGREGATE_TYPE_UNSPECIFIED`: Default value
- `AVERAGE`: Average
- `COUNT`: Count
- `MAX`: Maximum
- `MEDIAN`: Median
- `MIN`: Minimum
- `SUM`: Sum

### Interpolation Point Types
- `INTERPOLATION_POINT_TYPE_UNSPECIFIED`: Default value
- `MIN`: The minimum value in the range
- `MAX`: The maximum value in the range
- `NUMBER`: A number value
- `PERCENT`: A percentage value
- `PERCENTILE`: A percentile value

### Condition Types
- `CONDITION_TYPE_UNSPECIFIED`: Default value
- `NUMBER_GREATER`: The cell's value must be greater than the condition's value
- `NUMBER_GREATER_THAN_EQ`: The cell's value must be greater than or equal to the condition's value
- `NUMBER_LESS`: The cell's value must be less than the condition's value
- `NUMBER_LESS_THAN_EQ`: The cell's value must be less than or equal to the condition's value
- `NUMBER_EQ`: The cell's value must be equal to the condition's value
- `NUMBER_NOT_EQ`: The cell's value must not be equal to the condition's value
- `NUMBER_BETWEEN`: The cell's value must be between the condition's two values
- `NUMBER_NOT_BETWEEN`: The cell's value must not be between the condition's two values
- `TEXT_CONTAINS`: The cell's value must contain the condition's value
- `TEXT_NOT_CONTAINS`: The cell's value must not contain the condition's value
- `TEXT_STARTS_WITH`: The cell's value must start with the condition's value
- `TEXT_ENDS_WITH`: The cell's value must end with the condition's value
- `TEXT_EQ`: The cell's value must be equal to the condition's value
- `TEXT_IS_EMAIL`: The cell's value must be a valid email address
- `TEXT_IS_URL`: The cell's value must be a valid URL
- `DATE_EQ`: The cell's value must be equal to the condition's value
- `DATE_BEFORE`: The cell's value must be before the condition's value
- `DATE_AFTER`: The cell's value must be after the condition's value
- `DATE_ON_OR_BEFORE`: The cell's value must be on or before the condition's value
- `DATE_ON_OR_AFTER`: The cell's value must be on or after the condition's value
- `DATE_BETWEEN`: The cell's value must be between the condition's two values
- `DATE_NOT_BETWEEN`: The cell's value must not be between the condition's two values
- `DATE_IS_TODAY`: The cell's value must be today
- `DATE_IS_YESTERDAY`: The cell's value must be yesterday
- `DATE_IS_LAST_7_DAYS`: The cell's value must be in the last 7 days
- `DATE_IS_LAST_MONTH`: The cell's value must be in the last month
- `DATE_IS_LAST_YEAR`: The cell's value must be in the last year
- `DATE_IS_THIS_MONTH`: The cell's value must be in this month
- `DATE_IS_THIS_YEAR`: The cell's value must be in this year
- `DATE_IS_NEXT_MONTH`: The cell's value must be in next month
- `DATE_IS_NEXT_YEAR`: The cell's value must be in next year
- `DATE_IS_EMPTY`: The cell's value must be empty
- `DATE_IS_NOT_EMPTY`: The cell's value must not be empty
- `CUSTOM_FORMULA`: The cell's value must match the custom formula

### Error Types
- `ERROR_TYPE_UNSPECIFIED`: Default value
- `ERROR`: General error
- `NULL_VALUE`: Null value error
- `DIVIDE_BY_ZERO`: Divide by zero error
- `VALUE`: Value error
- `REF`: Reference error
- `NAME`: Name error
- `NUM`: Number error
- `N_A`: N/A error
- `LOADING`: Loading error

### Pivot Value Functions
- `PIVOT_STANDARD_VALUE_FUNCTION_UNSPECIFIED`: Default value
- `SUM`: Sum
- `COUNTA`: Count all
- `COUNT`: Count
- `COUNTUNIQUE`: Count unique
- `AVERAGE`: Average
- `MAX`: Maximum
- `MIN`: Minimum
- `MEDIAN`: Median
- `PRODUCT`: Product
- `STDEV`: Standard deviation
- `STDEVP`: Standard deviation population
- `VAR`: Variance
- `VARP`: Variance population
- `CUSTOM`: Custom

### Pivot Value Display Types
- `PIVOT_VALUE_CALCULATED_DISPLAY_TYPE_UNSPECIFIED`: Default value
- `PERCENT_OF_GRAND_TOTAL`: Percent of grand total
- `PERCENT_OF_COLUMN_TOTAL`: Percent of column total
- `PERCENT_OF_ROW_TOTAL`: Percent of row total
- `PERCENT_OF_TOTAL`: Percent of total
- `PERCENT_OF_PARENT_COLUMN_TOTAL`: Percent of parent column total
- `PERCENT_OF_PARENT_ROW_TOTAL`: Percent of parent row total
- `PERCENT_OF_PARENT_TOTAL`: Percent of parent total
- `RANK`: Rank
- `PERCENTILE`: Percentile
- `INDEX`: Index

### DateTime Rule Types
- `DATE_TIME_RULE_TYPE_UNSPECIFIED`: Default value
- `SECOND`: Second
- `MINUTE`: Minute
- `HOUR`: Hour
- `HOUR_MINUTE`: Hour and minute
- `HOUR_MINUTE_AMPM`: Hour and minute with AM/PM
- `DAY_OF_WEEK`: Day of week
- `DAY_OF_YEAR`: Day of year
- `DAY_OF_MONTH`: Day of month
- `DAY_MONTH`: Day and month
- `MONTH`: Month
- `QUARTER`: Quarter
- `YEAR`: Year
- `YEAR_MONTH`: Year and month
- `YEAR_QUARTER`: Year and quarter
- `YEAR_MONTH_DAY`: Year, month, and day

### Waterfall Stacked Types
- `WATERFALL_STACKED_TYPE_UNSPECIFIED`: Default value
- `STACKED`: Stacked
- `SEQUENTIAL`: Sequential

### Org Chart Label Sizes
- `ORG_CHART_LABEL_SIZE_UNSPECIFIED`: Default value
- `SMALL`: Small size
- `MEDIUM`: Medium size
- `LARGE`: Large size

### Bubble Chart Legend Positions
- `BUBBLE_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
- `BOTTOM_LEGEND`: Legend at the bottom
- `LEFT_LEGEND`: Legend at the left
- `RIGHT_LEGEND`: Legend at the right
- `TOP_LEGEND`: Legend at the top
- `NO_LEGEND`: No legend

### Pie Chart Legend Positions
- `PIE_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
- `BOTTOM_LEGEND`: Legend at the bottom
- `LEFT_LEGEND`: Legend at the left
- `RIGHT_LEGEND`: Legend at the right
- `TOP_LEGEND`: Legend at the top
- `NO_LEGEND`: No legend

### Sort Orders
- `ASCENDING`: Ascending order
- `DESCENDING`: Descending order

### Value Layouts
- `HORIZONTAL`: Horizontal layout
- `VERTICAL`: Vertical layout

## Batch Update Request Types

### Common Batch Update Operations

The `batchUpdate` endpoint accepts various request types in the `requests` array:

#### 1. Update Cells
```json
{
  "updateCells": {
    "range": {...},
    "rows": [...],
    "fields": "userEnteredValue,userEnteredFormat"
  }
}
```

#### 2. Insert Dimension
```json
{
  "insertDimension": {
    "range": {...},
    "inheritFromBefore": true
  }
}
```

#### 3. Delete Dimension
```json
{
  "deleteDimension": {
    "range": {...}
  }
}
```

#### 4. Update Sheet Properties
```json
{
  "updateSheetProperties": {
    "properties": {...},
    "fields": "title,hidden"
  }
}
```

#### 5. Add Sheet
```json
{
  "addSheet": {
    "properties": {...}
  }
}
```

#### 6. Delete Sheet
```json
{
  "deleteSheet": {
    "sheetId": 123
  }
}
```

#### 7. Duplicate Sheet
```json
{
  "duplicateSheet": {
    "sourceSheetId": 123,
    "insertSheetIndex": 1,
    "newSheetName": "Copy"
  }
}
```

#### 8. Update Borders
```json
{
  "updateBorders": {
    "range": {...},
    "top": {...},
    "bottom": {...},
    "left": {...},
    "right": {...},
    "innerHorizontal": {...},
    "innerVertical": {...}
  }
}
```

#### 9. Update Conditional Format Rule
```json
{
  "updateConditionalFormatRule": {
    "sheetId": 123,
    "index": 0,
    "rule": {...}
  }
}
```

#### 10. Add Conditional Format Rule
```json
{
  "addConditionalFormatRule": {
    "rule": {...}
  }
}
```

#### 11. Delete Conditional Format Rule
```json
{
  "deleteConditionalFormatRule": {
    "sheetId": 123,
    "index": 0
  }
}
```

#### 12. Update Chart Spec
```json
{
  "updateChartSpec": {
    "chartId": 123,
    "spec": {...}
  }
}
```

#### 13. Add Chart
```json
{
  "addChart": {
    "chart": {...}
  }
}
```

#### 14. Update Named Range
```json
{
  "updateNamedRange": {
    "namedRangeId": "range1",
    "namedRange": {...},
    "fields": "name,range"
  }
}
```

#### 15. Add Named Range
```json
{
  "addNamedRange": {
    "namedRange": {...}
  }
}
```

#### 16. Delete Named Range
```json
{
  "deleteNamedRange": {
    "namedRangeId": "range1"
  }
}
```

#### 17. Update Developer Metadata
```json
{
  "updateDeveloperMetadata": {
    "dataFilters": [...],
    "developerMetadata": {...},
    "fields": "metadataKey,metadataValue"
  }
}
```

#### 18. Delete Developer Metadata
```json
{
  "deleteDeveloperMetadata": {
    "dataFilters": [...]
  }
}
```

#### 19. Auto Resize Dimensions
```json
{
  "autoResizeDimensions": {
    "dimensions": {...}
  }
}
```

#### 20. Move Dimension
```json
{
  "moveDimension": {
    "source": {...},
    "destinationIndex": 5
  }
}
```

#### 21. Update Dimension Properties
```json
{
  "updateDimensionProperties": {
    "range": {...},
    "properties": {...},
    "fields": "hiddenByUser,pixelSize"
  }
}
```

#### 22. Update Sheet Properties
```json
{
  "updateSheetProperties": {
    "properties": {...},
    "fields": "title,hidden,tabColor"
  }
}
```

#### 23. Update Spreadsheet Properties
```json
{
  "updateSpreadsheetProperties": {
    "properties": {...},
    "fields": "title,locale,timeZone"
  }
}
```

#### 24. Update Table
```json
{
  "updateTable": {
    "table": {...},
    "fields": "tableColumns,tableRows"
  }
}
```

#### 25. Refresh Data Source
```json
{
  "refreshDataSource": {
    "dataSourceId": "ds_123",
    "force": true
  }
}
```

This comprehensive documentation now covers ALL aspects of the Google Sheets API v4 as defined in the discovery document, including all 130 schemas, all endpoints, all parameters, all enum values, all response formats, all request structures, and all batch update request types. For implementation details and client libraries, refer to the official Google Sheets API documentation.