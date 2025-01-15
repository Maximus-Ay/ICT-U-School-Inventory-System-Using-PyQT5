from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import Images
import sqlite3
from datetime import datetime

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

         # Populate ItemID2 ComboBox
        self.populate_item_ids()

        # Connect ComboBox selection change to update ItemName2 LineEdit
        self.ItemID2.currentIndexChanged.connect(self.update_item_name)

        # Connect Sign_Out button to the sign_out method
        self.Sign_Out.clicked.connect(self.sign_out)

        # Create TrackItems table if not exists
        self.create_track_items_table()

       # Connect Sign_In button to the sign_in method
        self.Sign_In.clicked.connect(self.sign_in)

        # Connect double-click on SignInSignOutTable to populate fields
        self.SignInSignOutTable.cellDoubleClicked.connect(self.populate_fields_for_sign_in)

        # Track selected row for updating
        self.selected_sign_in_row_data = None

        self.load_sign_in_sign_out_data()

        self.ClearBtn_2.clicked.connect(self.clear_fields)
        self.Delete.clicked.connect(self.delete_record)

        # Connect the search bar to the search function
        self.SearchBar_2.textChanged.connect(self.search_items2)

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


 #######################################################################################################
 #           SIGN IN SIGN OUT SECTION                                          
 # #####################################################################################################                   

    def populate_item_ids(self):
        """Populate the ItemID2 ComboBox with existing ItemIDs from the Inventory table."""
        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            cursor.execute("SELECT ItemID FROM Inventory")  # Query to get ItemIDs
            item_ids = cursor.fetchall()  # Fetch all ItemIDs

            # Clear the ComboBox first
            self.ItemID2.clear()

            # Add "Select Item" as the first option
            self.ItemID2.addItem("Select ItemID")

            # Populate the ComboBox with ItemIDs
            for item_id in item_ids:
                self.ItemID2.addItem(item_id[0])  # Add each ItemID to the ComboBox

            connection.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error populating ComboBox: {e}")

    def update_item_name(self):
        """Update the ItemName2 LineEdit based on the selected ItemID2."""
        item_id = self.ItemID2.currentText()  # Get selected ItemID

        if item_id == "Select Item":  # If the user selects the default option
            self.ItemName2.clear()
            return

        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            cursor.execute("SELECT ItemName FROM Inventory WHERE ItemID = ?", (item_id,))
            item_name = cursor.fetchone()  # Fetch the ItemName corresponding to the ItemID

            if item_name:
                self.ItemName2.setText(item_name[0])  # Update the LineEdit with the corresponding ItemName

            connection.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error updating ItemName: {e}")

    def create_track_items_table(self):
        """Create the TrackItems table if it does not already exist."""
        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS TrackItems (
                    ItemID TEXT,
                    ItemName TEXT,
                    ItemStatus TEXT,
                    ItemLocation TEXT,
                    QuantityOut INTEGER,
                    StudentMatricule TEXT,
                    Date TEXT
                )
            """)

            connection.commit()
            connection.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error creating TrackItems table: {e}")

    def sign_out(self):
        """Handle the Sign Out process by validating inputs and saving them to the database."""
        # Get the values from input fields
        item_id = self.ItemID2.currentText()
        item_name = self.ItemName2.text().strip()
        item_status = "Signed Out"
        item_location = self.ItemLocation.currentText()
        quantity_out = self.Quantity2.text().strip()
        student_matricule = self.StudentMatricule.text().strip()

        # Validate inputs
        if item_id == "Select ItemID":
            QMessageBox.warning(self, "Input Error", "Please select a valid ItemID.")
            return

        if not item_name:
            QMessageBox.warning(self, "Input Error", "Item Name cannot be empty.")
            return

        if item_status == "Item Status":
            QMessageBox.warning(self, "Input Error", "Please select a valid Item Status.")
            return

        if item_location == "Location":
            QMessageBox.warning(self, "Input Error", "Please select a valid Location.")
            return

        if not quantity_out.isdigit():
            QMessageBox.warning(self, "Input Error", "Quantity Out must be a number.")
            return
        
        # Check if the quantity is less than or equal to 0
        if int(quantity_out) <= 0:
            QMessageBox.warning(self, "Input Error", "Quantity Out must be greater than 0.")
            return

        if not student_matricule:
            QMessageBox.warning(self, "Input Error", "Student Matricule cannot be empty.")
            return

        # Get current date and time
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        quantity_out = int(quantity_out)

        try:
            # Save the data to the TrackItems table
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Subtract the quantity from the Inventory table
            cursor.execute("""
                UPDATE Inventory
                SET ItemQuantity = ItemQuantity - ?
                WHERE ItemID = ?
            """, (quantity_out, item_id))

            cursor.execute("""
                INSERT INTO TrackItems (ItemID, ItemName, ItemStatus, ItemLocation, QuantityOut, StudentMatricule, Date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item_name, item_status, item_location, int(quantity_out), student_matricule, current_date))

            connection.commit()
            connection.close()

            # Populate the SignInSignOutTable with the latest data
            self.load_sign_in_sign_out_data()
            self.clear_fields()
            self.load_table_data()

            QMessageBox.information(self, "Success", "Item successfully signed out!")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error saving data: {e}")

    def load_sign_in_sign_out_data(self):
        """Load the data from TrackItems table and populate the SignInSignOutTable."""
        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Fetch all records from the TrackItems table
            cursor.execute("SELECT * FROM TrackItems")
            rows = cursor.fetchall()

            # Clear the table first
            self.SignInSignOutTable.setRowCount(0)

            # Populate the table with data
            for row_data in rows:
                row_number = self.SignInSignOutTable.rowCount()
                self.SignInSignOutTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.SignInSignOutTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            connection.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading data: {e}")

    def populate_fields_for_sign_in(self, row, column):
        """Populate input fields with data from the selected row for Sign In."""
        self.selected_sign_in_row_data = []
        
        # Fetch data from the selected row in SignInSignOutTable
        for col in range(self.SignInSignOutTable.columnCount()):
            item = self.SignInSignOutTable.item(row, col)
            if item is not None:
                self.selected_sign_in_row_data.append(item.text())
            else:
                self.selected_sign_in_row_data.append("")  # Use empty string if no data

        # Populate input fields (excluding Date)
        self.ItemID2.setCurrentText(self.selected_sign_in_row_data[0])
        self.ItemName2.setText(self.selected_sign_in_row_data[1])
        self.ItemStatus.setCurrentText(self.selected_sign_in_row_data[2])  # Will be updated to "Signed In"
        self.ItemLocation.setCurrentText(self.selected_sign_in_row_data[3])
        self.Quantity2.setText(self.selected_sign_in_row_data[4])  # The quantity will be reset to 0 when signing in
        self.StudentMatricule.setText(self.selected_sign_in_row_data[5])

    def sign_in(self):
        """Handle the Sign In process by updating the selected record."""
        if not self.selected_sign_in_row_data:
            QMessageBox.warning(self, "Selection Error", "Please double-click a record to select it for Sign In.")
            return

        # Set the quantity to 0 for sign-in and update item status
        self.Quantity2.setText("0")  # Set Quantity to 0
        self.ItemStatus.setCurrentText("Signed In")  # Set Item Status to "Signed In"

        # Get updated data from the fields
        item_id = self.ItemID2.currentText()
        item_name = self.ItemName2.text().strip()
        item_status = self.ItemStatus.currentText()
        item_location = self.ItemLocation.currentText()
        quantity_in = 0  # Set quantity to 0 upon sign-in
        student_matricule = self.StudentMatricule.text().strip()
        quantity_out = self.selected_sign_in_row_data[4]  # Quantity used during sign-out

        # Validate inputs before saving
        if not item_id or not item_name or item_status == "Item Status" or item_location == "Location" or not student_matricule:
            QMessageBox.warning(self, "Input Error", "All fields must be filled out correctly.")
            return
        # Get the current date and time for the Date column
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Update the database with the new data
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Add back the quantity to the Inventory table
            cursor.execute("""
                UPDATE Inventory
                SET ItemQuantity = ItemQuantity + ?
                WHERE ItemID = ?
            """, (quantity_out, item_id))

            cursor.execute("""
                UPDATE TrackItems
                SET ItemName = ?, ItemStatus = ?, ItemLocation = ?, QuantityOut = ?, StudentMatricule = ?, Date = ?
                WHERE ItemID = ? AND Date = ?
            """, (item_name, item_status, item_location, quantity_in, student_matricule, current_date, item_id, self.selected_sign_in_row_data[6]))  # Using the Date from the selected row

            connection.commit()
            connection.close()

            # Refresh the SignInSignOutTable to reflect updated data
            self.load_sign_in_sign_out_data()
            self.clear_fields()
            self.load_table_data()

            QMessageBox.information(self, "Success", "Item successfully signed in!")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error updating data: {e}")

    def clear_fields(self):
        """Clear all fields and reset ComboBoxes to their default values."""
        self.ItemID2.setCurrentText("Select ItemID")  # Reset ComboBox to default
        self.ItemName2.clear()
        self.ItemStatus.setCurrentText("Item Status")  # Reset ComboBox to default
        self.ItemLocation.setCurrentText("Location")  # Reset ComboBox to default
        self.Quantity2.clear()
        self.StudentMatricule.clear()

    def delete_record(self):
        """Delete the selected record from the database."""
        if not self.selected_sign_in_row_data:
            QMessageBox.warning(self, "Selection Error", "Please double-click a record to select it for deletion.")
            return

        item_id = self.ItemID2.currentText()

        # Confirm the deletion
        reply = QMessageBox.question(self, "Delete Record", f"Are you sure you want to delete the record with ItemID {item_id}?", QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Delete the selected record from the database
                connection = sqlite3.connect("Inventory.db")
                cursor = connection.cursor()

                cursor.execute("""
                    DELETE FROM TrackItems
                    WHERE ItemID = ? AND Date = ?
                """, (item_id, self.selected_sign_in_row_data[6]))

                connection.commit()
                connection.close()

                # Refresh the table to reflect the deletion
                self.load_sign_in_sign_out_data()

                QMessageBox.information(self, "Success", "Record successfully deleted!")
                self.clear_fields()  # Clear fields after deletion

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Error deleting data: {e}")


    def search_items2(self):
        """Search the database for matches and update the QTableWidget."""
        search_text = self.SearchBar_2.text().strip().lower()  # Get and normalize search text

        try:
            connection = sqlite3.connect("Inventory.db")
            cursor = connection.cursor()

            # Query to search for matches in ItemID, ItemName, or Category
            query = """
                SELECT * FROM TrackItems
                WHERE LOWER(ItemID) LIKE ?
                OR LOWER(ItemName) LIKE ?
                OR LOWER(ItemStatus) LIKE ?
                OR LOWER(ItemLocation) LIKE ?
                OR LOWER(StudentMatricule) LIKE ?
            """
            search_pattern = f"%{search_text}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            rows = cursor.fetchall()

            # Update the QTableWidget with search results
            self.SignInSignOutTable.setRowCount(0)  # Clear the table
            for row_data in rows:
                row_number = self.SignInSignOutTable.rowCount()
                self.SignInSignOutTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.SignInSignOutTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            connection.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while searching: {e}")

