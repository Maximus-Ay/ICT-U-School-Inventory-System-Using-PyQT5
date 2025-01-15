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

        #creating the inventory table
        self.create_inventory_table()

        # loading database data, anytime the application is runned
        self.load_table_data()


    ##############################################
    #####    MOVE TO THE DASHBOARD ###############
    ##############################################
    def show_dashboard(self):
        """Switch to the Dashboard page."""
        self.stackedWidget.setCurrentIndex(0) 

    ##############################################
    #####    MOVE TO THE MODIFY ITEMS PAGE #######
    ##############################################
    def show_modify_items(self):
        """Switch to the Modify Items page."""
        self.stackedWidget.setCurrentIndex(1) 

    ##############################################
    #####    MOVE TO THE DASHBOARD ###############
    ##############################################
    def show_sign_in_sign_out(self):
        """Switch to the Sign In/Sign Out page."""
        self.stackedWidget.setCurrentIndex(2)  


    ##############################################
    ####    ADD ITEM FUNCTIONALITY        ########
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

            # Update the QTableWidget
            self.update_table(item_id, item_name, item_quantity, category, quantity_in_stock, description)

            # Clear input fields
            self.clear_inputs()

            QMessageBox.information(self, "Success", "Item added successfully!")

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Input Error", "Item ID already exists. Please use a unique ID.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

    def update_table(self, item_id, item_name, item_quantity, category, quantity_in_stock, description):
        """Add a new row to the QTableWidget with the provided item details."""
        row_position = self.ModifyItemsTable.rowCount()
        self.ModifyItemsTable.insertRow(row_position)

        self.ModifyItemsTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(item_id))
        self.ModifyItemsTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(item_name))
        self.ModifyItemsTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(item_quantity))
        self.ModifyItemsTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(category))
        self.ModifyItemsTable.setItem(row_position, 4, QtWidgets.QTableWidgetItem(quantity_in_stock))
        self.ModifyItemsTable.setItem(row_position, 5, QtWidgets.QTableWidgetItem(description))

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


    


