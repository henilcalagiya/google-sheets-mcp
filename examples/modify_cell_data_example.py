"""
Example usage of the modify_cell_data_tool

This example demonstrates how to modify specific cells in Google Sheets tables.
"""

# Example 1: Update single cell
def update_single_cell():
    """
    Update a single cell in the table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Employee Table",
        "cell_locations": ["A2"],
        "cell_values": ["Updated Name"]
    }

# Example 2: Update multiple cells
def update_multiple_cells():
    """
    Update multiple cells in the table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Employee Table",
        "cell_locations": ["A2", "D2", "C3"],
        "cell_values": ["John Smith", "55000", "Engineering"]
    }

# Example 3: Update project status
def update_project_status():
    """
    Update project status in a project tracker table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Project Tracker",
        "cell_locations": ["B1", "B2", "B3"],
        "cell_values": ["Completed", "In Progress", "On Hold"]
    }

# Example 4: Update employee salary
def update_employee_salary():
    """
    Update employee salary information.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Employee Table",
        "cell_locations": ["D2", "D3", "D4"],
        "cell_values": ["65000", "70000", "58000"]
    }

# Example 5: Update inventory quantities
def update_inventory_quantities():
    """
    Update inventory quantities in an inventory table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Inventory",
        "cell_locations": ["C1", "C2", "C3"],
        "cell_values": ["45", "180", "60"]
    }

# Example 6: Update sales figures
def update_sales_figures():
    """
    Update sales figures in a sales table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Sales Data",
        "cell_locations": ["B1", "D1", "B2", "D2"],
        "cell_values": ["175", "4548.25", "85", "3867.50"]
    }

# Example 7: Update contact information
def update_contact_info():
    """
    Update contact information in a contacts table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Contacts",
        "cell_locations": ["B2", "C2", "B3", "C3"],
        "cell_values": ["john.smith@company.com", "+1-555-0123", "jane.doe@company.com", "+1-555-0456"]
    }

# Example 8: Update task priorities
def update_task_priorities():
    """
    Update task priorities in a task management table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Task List",
        "cell_locations": ["C1", "C2", "C3", "C4"],
        "cell_values": ["High", "Medium", "Low", "Critical"]
    }

# Example 9: Update order status
def update_order_status():
    """
    Update order status in an orders table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Orders",
        "cell_locations": ["B1", "B2", "B3", "B4"],
        "cell_values": ["Shipped", "Processing", "Delivered", "Cancelled"]
    }

# Example 10: Update budget allocations
def update_budget_allocations():
    """
    Update budget allocations in a budget table.
    """
    return {
        "spreadsheet_name": "My Projects",
        "sheet_name": "Sheet1",
        "table_name": "Budget",
        "cell_locations": ["C1", "C2", "C3", "C4"],
        "cell_values": ["50000", "75000", "25000", "100000"]
    }

if __name__ == "__main__":
    print("Modify Cell Data Examples")
    print("=" * 50)
    print()
    print("1. Update single cell:", update_single_cell())
    print("2. Update multiple cells:", update_multiple_cells())
    print("3. Update project status:", update_project_status())
    print("4. Update employee salary:", update_employee_salary())
    print("5. Update inventory quantities:", update_inventory_quantities())
    print("6. Update sales figures:", update_sales_figures())
    print("7. Update contact info:", update_contact_info())
    print("8. Update task priorities:", update_task_priorities())
    print("9. Update order status:", update_order_status())
    print("10. Update budget allocations:", update_budget_allocations()) 