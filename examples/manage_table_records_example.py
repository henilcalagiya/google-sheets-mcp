"""
Example usage of the manage_table_records_tool

This example demonstrates how to manage table records in Google Sheets.
"""

# Example 1: Append rows to table
def append_rows():
    """
    Append new rows at the end of the table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Employee Table",
        "operation": "append",
        "data": [
            ["John Doe", "30", "HR", "50000"],
            ["Jane Smith", "25", "IT", "60000"],
            ["Bob Johnson", "35", "Sales", "55000"]
        ]
    }

# Example 2: Insert rows at specific position
def insert_rows():
    """
    Insert rows at a specific position in the table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Employee Table",
        "operation": "insert",
        "row_index": 2,  # Insert after the 3rd data row (0-based, header excluded)
        "data": [
            ["Alice Brown", "28", "Marketing", "52000"],
            ["Charlie Wilson", "32", "Engineering", "65000"]
        ]
    }

# Example 3: Remove specific rows
def remove_rows():
    """
    Remove specific rows from the table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Employee Table",
        "operation": "remove",
        "row_indices": [1, 3]  # Remove 2nd and 4th data rows (0-based, header excluded)
    }

# Example 4: Append project data
def append_project_data():
    """
    Append new project data to a project tracker table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "operation": "append",
        "data": [
            ["Website Redesign", "In Progress", "High", "2024-03-15", "John Doe"],
            ["Mobile App", "Planning", "Medium", "2024-04-01", "Jane Smith"],
            ["Database Migration", "Completed", "Low", "2024-02-28", "Bob Johnson"]
        ]
    }

# Example 5: Insert priority project
def insert_priority_project():
    """
    Insert a high-priority project at the top of the list.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "operation": "insert",
        "row_index": 0,  # Insert at the very beginning (after header)
        "data": [
            ["Emergency Bug Fix", "Urgent", "Critical", "2024-03-10", "Alice Brown"]
        ]
    }

# Example 6: Remove completed projects
def remove_completed_projects():
    """
    Remove completed projects from the tracker.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "operation": "remove",
        "row_indices": [2, 5, 8]  # Remove 3rd, 6th, and 9th data rows (0-based, header excluded)
    }

# Example 7: Append sales data
def append_sales_data():
    """
    Append new sales records to a sales table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Sales Data",
        "operation": "append",
        "data": [
            ["Product A", "150", "25.99", "3898.50", "2024-03-01"],
            ["Product B", "75", "45.50", "3412.50", "2024-03-01"],
            ["Product C", "200", "12.99", "2598.00", "2024-03-01"]
        ]
    }

# Example 8: Insert urgent order
def insert_urgent_order():
    """
    Insert an urgent order at the top of the orders list.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Orders",
        "operation": "insert",
        "row_index": 0,
        "data": [
            ["URGENT-001", "Express Delivery", "High Priority", "2024-03-01", "Immediate"]
        ]
    }

# Example 9: Remove outdated records
def remove_outdated_records():
    """
    Remove outdated records from the table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Historical Data",
        "operation": "remove",
        "row_indices": [0, 1, 2, 3, 4]  # Remove first 5 data rows (0-based, header excluded)
    }

# Example 10: Append inventory update
def append_inventory_update():
    """
    Append new inventory items to the inventory table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Inventory",
        "operation": "append",
        "data": [
            ["Laptop", "Electronics", "50", "999.99", "In Stock"],
            ["Mouse", "Electronics", "200", "25.50", "In Stock"],
            ["Keyboard", "Electronics", "75", "89.99", "Low Stock"]
        ]
    }

if __name__ == "__main__":
    print("Manage Table Records Examples")
    print("=" * 50)
    print()
    print("1. Append rows:", append_rows())
    print("2. Insert rows:", insert_rows())
    print("3. Remove rows:", remove_rows())
    print("4. Append project data:", append_project_data())
    print("5. Insert priority project:", insert_priority_project())
    print("6. Remove completed projects:", remove_completed_projects())
    print("7. Append sales data:", append_sales_data())
    print("8. Insert urgent order:", insert_urgent_order())
    print("9. Remove outdated records:", remove_outdated_records())
    print("10. Append inventory update:", append_inventory_update()) 