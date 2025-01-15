from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import Images
import sqlite3

class InventorySysWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Load the Inventory System UI
        uic.loadUi("InventorySys.ui", self)

        # Connect buttons to their respective functions
        self.DashboardBtn.clicked.connect(self.show_dashboard)
        self.ModifyItemsBtn.clicked.connect(self.show_modify_items)
        self.SignInSignOutBtn.clicked.connect(self.show_sign_in_sign_out)

        # Connect the AddItem button to the add_item method
        self.AddItemBtn.clicked.connect(self.add_item)

        # connect to the clear inputs button
        self.ClearBtn.clicked.connect(self.clear_inputs)

        self.UpdateItemBtn.clicked.connect(self.update_item)

        self.DeleteItem.clicked.connect(self.delete_item)

        self.SearchBar.textChanged.connect(self.search_items)

        #creating the inventory table
        self.create_inventory_table()

        # loading database data, anytime the application is runned
        self.load_table_data()

        # Connect the QTableWidget item double-click signal
        self.ModifyItemsTable.cellDoubleClicked.connect(self.populate_fields_for_update)

        # Track selected item for update or delete
        self.selected_row_data = None

    ##############################################
    #####    MOVE TO THE DASHBOARD 
    ##############################################
    def show_dashboard(self):
        """Switch to the Dashboard page."""
        self.stackedWidget.setCurrentIndex(0) 

    ##############################################
    #####    MOVE TO THE MODIFY ITEMS PAGE 
    ##############################################
    def show_modify_items(self):
        """Switch to the Modify Items page."""
        self.stackedWidget.setCurrentIndex(1) 

    ##############################################
    #####    MOVE TO THE DASHBOARD 
    ##############################################
    def show_sign_in_sign_out(self):
        """Switch to the Sign In/Sign Out page."""
        self.stackedWidget.setCurrentIndex(2)  


    ##############################################
    ####    ADD ITEM FUNCTIONALITY        
    ##############################################

    def create_inventory_table(self):
        """Create the Inventory table if it does not already exist."""
        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Inventory (
                    ItemID TEXT PRIMARY KEY,
                    ItemName TEXT NOT NULL,
                    ItemQuantity INTEGER NOT NULL,
                    Category TEXT NOT NULL,
                    QuantityInStock INTEGER NOT NULL,
                    Description TEXT
                )
            """)

            connection.commit()
            connection.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error creating table: {e}")

    def add_item(self):
        """Validate inputs, add item to database, and update the table."""
        # Validate inputs
        item_id = self.ItemID.text().strip()
        item_name = self.ItemName.text().strip()
        item_quantity = self.ItemQty.text().strip()
        category = self.Category.currentText()
        quantity_in_stock = self.QtyInStock.text().strip()
        description = self.Description.text().strip()

        if not item_id or not any(c.isalnum() for c in item_id):
            QMessageBox.warning(self, "Input Error", "Item ID cannot be empty and must contain letters and/or numbers.")
            return

        if not item_name or not all(c.isalpha() or c.isspace() for c in item_name):
            QMessageBox.warning(self, "Input Error", "Item Name cannot be empty and must contain only letters.")
            return

        if not item_quantity.isdigit():
            QMessageBox.warning(self, "Input Error", "Item Quantity must be a number.")
            return

        if category == "Category":
            QMessageBox.warning(self, "Input Error", "Please select a valid category.")
            return

        if not quantity_in_stock.isdigit():
            QMessageBox.warning(self, "Input Error", "Quantity in Stock must be a number.")
            return

        # Add to database
        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO Inventory (ItemID, ItemName, ItemQuantity, Category, QuantityInStock, Description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item_id, item_name, int(item_quantity), category, int(quantity_in_stock), description))

            connection.commit()
            connection.close()

            # Clear input fields
            self.clear_inputs()

            self.load_table_data()

            QMessageBox.information(self, "Success", "Item added successfully!")

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Input Error", "Item ID already exists. Please use a unique ID.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def clear_inputs(self):
        """Clear all input fields after adding an item."""
        self.ItemID.clear()
        self.ItemName.clear()
        self.ItemQty.clear()
        self.Category.setCurrentIndex(0)  # Reset to "Category"
        self.QtyInStock.clear()
        self.Description.clear()

    def load_table_data(self):
        """Load data from the database into the QTableWidget."""
        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Fetch all records from the Inventory table
            cursor.execute("SELECT * FROM Inventory")
            rows = cursor.fetchall()

            # Populate the QTableWidget
            self.ModifyItemsTable.setRowCount(0)  # Clear existing rows
            for row_data in rows:
                row_number = self.ModifyItemsTable.rowCount()
                self.ModifyItemsTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.ModifyItemsTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            connection.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading data: {e}")

    def populate_fields_for_update(self, row, column):
        """Populate input fields with data from the selected row."""
    # Initialize selected_row_data as an empty list
        self.selected_row_data = []

        for col in range(self.ModifyItemsTable.columnCount()):
            item = self.ModifyItemsTable.item(row, col)  # Get the QTableWidgetItem
            if item is not None:  # Check if the cell is not empty
                self.selected_row_data.append(item.text())
            else:
                self.selected_row_data.append("")  # Use an empty string for empty cells
            # Populate input fields

        self.ItemID.setText(self.selected_row_data[0])
        self.ItemName.setText(self.selected_row_data[1])
        self.ItemQty.setText(self.selected_row_data[2])
        self.Category.setCurrentText(self.selected_row_data[3])
        self.QtyInStock.setText(self.selected_row_data[4])
        self.Description.setText(self.selected_row_data[5])

    def update_item(self):
        """Update the selected item in the database."""
        if not self.selected_row_data:
            QMessageBox.warning(self, "Update Error", "Double click on record to update.")
            return

        # Get updated inputs
        item_id = self.ItemID.text().strip()
        item_name = self.ItemName.text().strip()
        item_quantity = self.ItemQty.text().strip()
        category = self.Category.currentText()
        quantity_in_stock = self.QtyInStock.text().strip()
        description = self.Description.text().strip()

        # Validate inputs (reuse add_item logic)
        if not item_id or not any(c.isalnum() for c in item_id):
            QMessageBox.warning(self, "Input Error", "Item ID cannot be empty and must contain letters and/or numbers.")
            return

        if not item_name or not all(c.isalpha() or c.isspace() for c in item_name):
            QMessageBox.warning(self, "Input Error", "Item Name cannot be empty and must contain only letters.")
            return

        if not item_quantity.isdigit():
            QMessageBox.warning(self, "Input Error", "Item Quantity must be a number.")
            return

        if category == "Category":
            QMessageBox.warning(self, "Input Error", "Please select a valid category.")
            return

        if not quantity_in_stock.isdigit():
            QMessageBox.warning(self, "Input Error", "Quantity in Stock must be a number.")
            return

        # Update the database
        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE Inventory
                SET ItemName = ?, ItemQuantity = ?, Category = ?, QuantityInStock = ?, Description = ?
                WHERE ItemID = ?
            """, (item_name, int(item_quantity), category, int(quantity_in_stock), description, item_id))

            connection.commit()
            connection.close()

            # Refresh the table
            self.load_table_data()

            # Clear the selected row and input fields
            self.selected_row_data = None
            self.clear_inputs()

            QMessageBox.information(self, "Success", "Item updated successfully!")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error updating item: {e}")

    def delete_item(self):
        """Delete the selected item from the database."""
        if not self.selected_row_data:
            QMessageBox.warning(self, "Delete Error", "Double click on record to delete.")
            return

        item_id = self.selected_row_data[0]  # Get the ItemID of the selected row

        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the item with ID '{item_id}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return

        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            cursor.execute("DELETE FROM Inventory WHERE ItemID = ?", (item_id,))
            connection.commit()
            connection.close()

            # Refresh the table
            self.load_table_data()

            # Clear the selected row and input fields
            self.selected_row_data = None
            self.clear_inputs()

            QMessageBox.information(self, "Success", "Item deleted successfully!")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error deleting item: {e}")

    
    def search_items(self):
        """Search the database for matches and update the QTableWidget."""
        search_text = self.SearchBar.text().strip().lower()  # Get and normalize search text

        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Query to search for matches in ItemID, ItemName, or Category
            query = """
                SELECT * FROM Inventory
                WHERE LOWER(ItemID) LIKE ? OR
                      LOWER(ItemName) LIKE ? OR
                      LOWER(Category) LIKE ?
            """
            search_pattern = f"%{search_text}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            rows = cursor.fetchall()

            # Update the QTableWidget with search results
            self.ModifyItemsTable.setRowCount(0)  # Clear the table
            for row_data in rows:
                row_number = self.ModifyItemsTable.rowCount()
                self.ModifyItemsTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.ModifyItemsTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            connection.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while searching: {e}")

