# Google Sheets API v4 - Schemas Reference

## 📋 Overview

This document provides a comprehensive reference for all 130 schemas in the Google Sheets API v4, organized by category for easy navigation.

## 🏗️ Core Data Structures

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
The request for clearing a range of values in a spreadsheet.

**Properties:**
- `spreadsheetId` (string): The ID of the spreadsheet to clear data from
- `range` (string): The A1 notation of the values to clear

### 5. ClearValuesResponse
The response when clearing a range of values in a spreadsheet.

**Properties:**
- `spreadsheetId` (string): The spreadsheet the updates were applied to
- `clearedRange` (string): The range (in A1 notation) that was cleared

## 📊 Spreadsheet Structures

### 6. Spreadsheet
Resource that represents a Google Sheets spreadsheet.

**Properties:**
- `spreadsheetId` (string): The ID of the spreadsheet
- `properties` (SpreadsheetProperties): Overall properties of a spreadsheet
- `sheets` (array): The sheets that are part of the spreadsheet
- `namedRanges` (array): The named ranges defined in a spreadsheet
- `developerMetadata` (array): The developer metadata associated with a spreadsheet
- `dataSources` (array): Data sources refresh in the spreadsheet

### 7. SpreadsheetProperties
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

### 8. SheetProperties
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

### 9. GridProperties
Properties of a grid.

**Properties:**
- `rowCount` (integer): The number of rows in the grid
- `columnCount` (integer): The number of columns in the grid
- `frozenRowCount` (integer): The number of rows that are frozen in the grid
- `frozenColumnCount` (integer): The number of columns that are frozen in the grid
- `hideGridlines` (boolean): True if the gridlines are hidden
- `rowGroupControlAfter` (boolean): True if the row group control is shown after the group
- `columnGroupControlAfter` (boolean): True if the column group control is shown after the group

## 🎨 Cell and Formatting Structures

### 10. CellData
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

### 11. CellFormat
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

### 12. ExtendedValue
The kinds of value that a cell can have.

**Properties:**
- `numberValue` (number): Represents a double value
- `stringValue` (string): Represents a string value
- `boolValue` (boolean): Represents a boolean value
- `formulaValue` (string): Represents a formula
- `errorValue` (ErrorValue): Represents an error

### 13. NumberFormat
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

### 14. TextFormat
The format of the text in the cell.

**Properties:**
- `foregroundColor` (Color): The foreground color of the text
- `fontFamily` (string): The font family of the text
- `fontSize` (integer): The size of the font
- `bold` (boolean): True if the text is bold
- `italic` (boolean): True if the text is italic
- `strikethrough` (boolean): True if the text has a strikethrough
- `underline` (boolean): True if the text is underlined

### 15. Color
A color value.

**Properties:**
- `red` (number): The amount of red in the color as a value in the interval [0, 1]
- `green` (number): The amount of green in the color as a value in the interval [0, 1]
- `blue` (number): The amount of blue in the color as a value in the interval [0, 1]
- `alpha` (number): The fraction of this color that should be applied to the pixel

### 16. Borders
The borders of a cell.

**Properties:**
- `top` (Border): The top border of the cell
- `bottom` (Border): The bottom border of the cell
- `left` (Border): The left border of the cell
- `right` (Border): The right border of the cell

### 17. Border
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

### 18. Padding
The amount of padding around the cell.

**Properties:**
- `top` (integer): The top padding of the cell
- `right` (integer): The right padding of the cell
- `bottom` (integer): The bottom padding of the cell
- `left` (integer): The left padding of the cell

## 📊 Range and Grid Structures

### 19. GridRange
A range on a sheet. All indexes are zero-based.

**Properties:**
- `sheetId` (integer): The sheet this range is on
- `startRowIndex` (integer): The start row (inclusive) of the range
- `endRowIndex` (integer): The end row (exclusive) of the range
- `startColumnIndex` (integer): The start column (inclusive) of the range
- `endColumnIndex` (integer): The end column (exclusive) of the range

### 20. DimensionRange
A range along a single dimension on a sheet.

**Properties:**
- `sheetId` (integer): The sheet this range is on
- `dimension` (string): The dimension of the range
  - `DIMENSION_UNSPECIFIED`: Default value
  - `ROWS`: Rows
  - `COLUMNS`: Columns
- `startIndex` (integer): The start (inclusive) of the range
- `endIndex` (integer): The end (exclusive) of the range

### 21. GridCoordinate
A coordinate in a sheet.

**Properties:**
- `sheetId` (integer): The sheet this coordinate is on
- `rowIndex` (integer): The row index of the coordinate
- `columnIndex` (integer): The column index of the coordinate

## 📈 Chart Structures

### 22. Chart
A chart embedded in a sheet.

**Properties:**
- `chartId` (integer): The ID of the chart
- `spec` (ChartSpec): The specifications of the chart
- `position` (EmbeddedObjectPosition): The position of the chart

### 23. ChartSpec
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

### 24. BasicChartSpec
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

### 25. ChartData
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

## 🔗 Named Ranges and References

### 26. NamedRange
A named range.

**Properties:**
- `namedRangeId` (string): The ID of the named range
- `name` (string): The name of the named range
- `range` (GridRange): The range this named range covers

## 📋 Conditional Formatting

### 27. ConditionalFormatRule
A rule describing a conditional format.

**Properties:**
- `ranges` (array): The ranges that are formatted if the condition is true
- `booleanRule` (BooleanRule): The formatting is either "on" or "off" according to the rule
- `gradientRule` (GradientRule): The formatting will vary based on the values in each cell

### 28. BooleanRule
A rule that may or may not match, requiring a formula to evaluate.

**Properties:**
- `condition` (BooleanCondition): The condition of the rule
- `format` (CellFormat): The format to apply to the cell

### 29. BooleanCondition
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

### 30. GradientRule
A rule that applies a gradient color scale to a cell or range.

**Properties:**
- `minpoint` (InterpolationPoint): The interpolation point for the minimum value
- `midpoint` (InterpolationPoint): The interpolation point for the midpoint value
- `maxpoint` (InterpolationPoint): The interpolation point for the maximum value

### 31. InterpolationPoint
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

## 🔧 Developer Metadata

### 32. DeveloperMetadata
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

### 33. DeveloperMetadataLocation
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

## 📊 Data Sources and BigQuery

### 34. DataSource
A data source.

**Properties:**
- `dataSourceId` (string): The ID of the data source
- `spec` (DataSourceSpec): The specification of the data source
- `calculatedColumns` (array): The calculated columns for the data source
- `sheets` (array): The sheets that are part of the data source

### 35. DataSourceSpec
The specification of a data source.

**Properties:**
- `parameters` (array): The parameters of the data source
- `bigQuery` (BigQueryDataSourceSpec): A BigQuery data source specification

### 36. BigQueryDataSourceSpec
The specification for a BigQuery data source.

**Properties:**
- `projectId` (string): The ID of the BigQuery project
- `querySpec` (BigQueryQuerySpec): The BigQuery query specification
- `tableSpec` (BigQueryTableSpec): The BigQuery table specification

## 📋 Tables and Data Validation

### 37. Table
A table in a sheet.

**Properties:**
- `tableId` (integer): The ID of the table
- `displayName` (string): The display name of the table
- `range` (GridRange): The range the table covers
- `columnCount` (integer): The number of columns in the table
- `rows` (array): The rows in the table
- `columns` (array): The columns in the table
- `style` (TableStyle): The style of the table

### 38. DataValidationRule
A data validation rule.

**Properties:**
- `condition` (BooleanCondition): The condition that data in the cell must match
- `inputMessage` (string): A message to show the user when adding data to the cell
- `strict` (boolean): True if the data validation rule should reject invalid data
- `showCustomUi` (boolean): True if the data validation rule should show custom help text

## 🔄 Batch Update Structures

### 39. BatchUpdateSpreadsheetRequest
The request for updating any aspect of a spreadsheet.

**Properties:**
- `requests` (array): A list of updates to apply to the spreadsheet
- `includeSpreadsheetInResponse` (boolean): Determines if the update response should include the spreadsheet resource
- `responseRanges` (array): Limits the ranges included in the response spreadsheet
- `responseIncludeGridData` (boolean): True if grid data should be returned

### 40. BatchUpdateSpreadsheetResponse
The response for updating a spreadsheet.

**Properties:**
- `spreadsheetId` (string): The reply of the updates
- `replies` (array): The reply of the updates
- `updatedSpreadsheet` (Spreadsheet): The spreadsheet after updates were applied

## 🔗 Related Documentation

- **[Complete Reference](00_Complete_Reference.md)** - All 130 schemas in detail
- **[API Overview](01_API_Overview.md)** - Basic API information
- **[Endpoints Reference](02_Endpoints_Reference.md)** - All API endpoints
- **[Batch Operations](04_Batch_Operations.md)** - Batch update operations
- **[Error Handling](10_Error_Handling.md)** - Error codes and troubleshooting

---

*This document provides a high-level overview of the key schemas. For complete details on all 130 schemas, see the [Complete Reference](00_Complete_Reference.md).* 