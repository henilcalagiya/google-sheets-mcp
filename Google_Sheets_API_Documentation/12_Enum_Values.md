# Google Sheets API v4 - Enum Values Reference

## 📋 Overview

This document provides a comprehensive reference for all enum values in the Google Sheets API v4, organized by category for easy lookup.

## 🔄 Data Organization

### Major Dimensions
- `DIMENSION_UNSPECIFIED`: Default value, do not use
- `ROWS`: Operates on the rows of a sheet
- `COLUMNS`: Operates on the columns of a sheet

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

## 🎨 Formatting and Alignment

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

## 📊 Number Formats

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

## 🎨 Borders and Colors

### Border Styles
- `STYLE_UNSPECIFIED`: Default value
- `DOTTED`: Dotted style
- `DASHED`: Dashed style
- `SOLID`: Solid style
- `SOLID_MEDIUM`: Solid medium style
- `SOLID_THICK`: Solid thick style
- `NONE`: No border
- `DOUBLE`: Double border

## 📈 Charts

### Basic Chart Types
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

### Pie Chart Legend Positions
- `PIE_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
- `BOTTOM_LEGEND`: Legend at the bottom
- `LEFT_LEGEND`: Legend at the left
- `RIGHT_LEGEND`: Legend at the right
- `TOP_LEGEND`: Legend at the top
- `NO_LEGEND`: No legend

### Bubble Chart Legend Positions
- `BUBBLE_CHART_LEGEND_POSITION_UNSPECIFIED`: Default value
- `BOTTOM_LEGEND`: Legend at the bottom
- `LEFT_LEGEND`: Legend at the left
- `RIGHT_LEGEND`: Legend at the right
- `TOP_LEGEND`: Legend at the top
- `NO_LEGEND`: No legend

### Org Chart Label Sizes
- `ORG_CHART_LABEL_SIZE_UNSPECIFIED`: Default value
- `SMALL`: Small size
- `MEDIUM`: Medium size
- `LARGE`: Large size

### Waterfall Stacked Types
- `WATERFALL_STACKED_TYPE_UNSPECIFIED`: Default value
- `STACKED`: Stacked
- `SEQUENTIAL`: Sequential

## 📋 Conditional Formatting

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

### Interpolation Point Types
- `INTERPOLATION_POINT_TYPE_UNSPECIFIED`: Default value
- `MIN`: The minimum value in the range
- `MAX`: The maximum value in the range
- `NUMBER`: A number value
- `PERCENT`: A percentage value
- `PERCENTILE`: A percentile value

## 🔧 Developer Metadata

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

## 📊 Sheets and Dimensions

### Sheet Types
- `SHEET_TYPE_UNSPECIFIED`: Default value
- `GRID`: A normal sheet
- `OBJECT`: An object sheet

### Dimensions
- `DIMENSION_UNSPECIFIED`: Default value
- `ROWS`: Rows
- `COLUMNS`: Columns

## 🔄 Recalculation

### Recalculation Interval
- `RECALCULATION_INTERVAL_UNSPECIFIED`: Default value
- `ON_CHANGE`: Volatile functions are recalculated on every change
- `MINUTE`: Volatile functions are recalculated on every minute
- `HOUR`: Volatile functions are recalculated on every hour

## 📈 Pivot Tables

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

### Value Layouts
- `HORIZONTAL`: Horizontal layout
- `VERTICAL`: Vertical layout

## 📅 DateTime Rules

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

## ⚠️ Error Types

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

## 🔄 Sort Orders

### Sort Orders
- `ASCENDING`: Ascending order
- `DESCENDING`: Descending order

## 📊 Insert Data Options

### Insert Data Options
- `INSERT_DATA_OPTION_UNSPECIFIED`: Default value
- `OVERWRITE`: Overwrite existing data
- `INSERT_ROWS`: Insert new rows

## 🔗 Related Documentation

- **[Complete Reference](00_Complete_Reference.md)** - All schemas and detailed information
- **[API Overview](01_API_Overview.md)** - Basic API information
- **[Schemas Reference](03_Schemas_Reference.md)** - Schema definitions
- **[Error Handling](10_Error_Handling.md)** - Error codes and troubleshooting
- **[Request Examples](13_Request_Examples.md)** - Common request patterns

---

*This document provides a comprehensive reference for all enum values in the Google Sheets API v4. Use these values when constructing API requests and handling responses.* 