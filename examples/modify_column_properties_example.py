"""
Example usage of the modify_column_properties_tool

This example demonstrates how to modify column properties in existing tables in Google Sheets.
"""

# Example 1: Change column name
def change_column_name():
    """
    Change the name of a column from 'Status' to 'Current Status'.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Status",
        "new_column_name": "Current Status"
    }

# Example 2: Change column type
def change_column_type():
    """
    Change a column type from TEXT to NUMBER.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Priority",
        "new_column_type": "NUMBER"
    }

# Example 3: Add dropdown validation
def add_dropdown_validation():
    """
    Add dropdown validation to a text column.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Department",
        "new_dropdown_options": ["Engineering", "Marketing", "Sales", "HR", "Finance"]
    }

# Example 4: Update dropdown options
def update_dropdown_options():
    """
    Update existing dropdown options for a column.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Status",
        "new_dropdown_options": ["Not Started", "In Progress", "Review", "Complete", "On Hold"]
    }

# Example 5: Remove dropdown validation
def remove_dropdown_validation():
    """
    Remove dropdown validation from a column.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Department",
        "remove_dropdown": True
    }

# Example 6: Change multiple properties at once
def change_multiple_properties():
    """
    Change column name, type, and dropdown options in one operation.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Priority",
        "new_column_name": "Priority Level",
        "new_column_type": "DROPDOWN",
        "new_dropdown_options": ["Low", "Medium", "High", "Critical"]
    }

# Example 7: Change date column type
def change_date_column():
    """
    Change a column from DATE to DATE_TIME.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Due Date",
        "new_column_type": "DATE_TIME"
    }

# Example 8: Change currency column
def change_currency_column():
    """
    Change a column from NUMBER to CURRENCY.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Budget",
        "new_column_type": "CURRENCY"
    }

# Example 9: Change percentage column
def change_percentage_column():
    """
    Change a column from NUMBER to PERCENT.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Progress",
        "new_column_type": "PERCENT"
    }

# Example 10: Change boolean column
def change_boolean_column():
    """
    Change a column from TEXT to BOOLEAN.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Completed",
        "new_column_type": "BOOLEAN"
    }

# Example 11: Add dropdown options to existing dropdown
def add_dropdown_options():
    """
    Add new options to an existing dropdown without replacing all options.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Department",
        "add_dropdown_options": ["Finance", "Legal"]  # Add these to existing options
    }

# Example 12: Remove specific dropdown options
def remove_dropdown_options():
    """
    Remove specific options from an existing dropdown.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Department",
        "remove_dropdown_options": ["HR", "Legal"]  # Remove these from existing options
    }

# Example 13: Add and remove options simultaneously
def modify_dropdown_options():
    """
    Add some options and remove others in one operation.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "column_name": "Department",
        "add_dropdown_options": ["Finance", "Operations"],
        "remove_dropdown_options": ["HR", "Legal"]
    }

# Example 10: Test that changing column name doesn't affect other column types
print("\n=== Example 10: Test Column Name Change (Preserve Other Columns) ===")
print("This test verifies that changing one column name doesn't affect other column types")
print("Expected: Only the target column name changes, other columns keep their types")

# First, let's check the current state of all columns
print("\nCurrent table state:")
# You would need to implement a tool to get current column properties
# For now, we'll just test the name change

# Change just the name of the first column
# Note: This is just an example - the actual tool call would be:
# result = modify_column_properties_tool(
#     spreadsheet_name="Test Spreadsheet",
#     sheet_name="Sheet1", 
#     table_name="Employee Table",
#     column_name="Name",  # Assuming this column exists
#     new_column_name="Full Name"
# )
# 
# print(f"Result: {result}")
# print("Expected: Only 'Name' column becomes 'Full Name', other columns unchanged")

if __name__ == "__main__":
    print("Modify Column Properties Examples")
    print("=" * 50)
    print()
    print("1. Change column name:", change_column_name())
    print("2. Change column type:", change_column_type())
    print("3. Add dropdown validation:", add_dropdown_validation())
    print("4. Update dropdown options:", update_dropdown_options())
    print("5. Remove dropdown validation:", remove_dropdown_validation())
    print("6. Change multiple properties:", change_multiple_properties())
    print("7. Change date column:", change_date_column())
    print("8. Change currency column:", change_currency_column())
    print("9. Change percentage column:", change_percentage_column())
    print("10. Change boolean column:", change_boolean_column())
    print("11. Add dropdown options:", add_dropdown_options())
    print("12. Remove dropdown options:", remove_dropdown_options())
    print("13. Modify dropdown options:", modify_dropdown_options()) 