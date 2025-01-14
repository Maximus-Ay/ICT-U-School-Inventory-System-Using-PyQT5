from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import myassets

class LoginWindow(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        # Load the Login UI
        uic.loadUi("Login.ui", self)
        self.stacked_widget = stacked_widget

        # Connect the login button to the validation function
        self.login_btn.clicked.connect(self.handle_login)

    ##################################################################################
    #####              FUNCTION TO HANDLE LOGIN                              #########
    ##################################################################################

    def handle_login(self):
        """Validate login credentials and navigate to the Inventory System."""
        username = self.Username_LineEdit.text()
        password = self.Password_LineEdit.text()

        if self.validate_credentials(username, password):
            self.stacked_widget.setCurrentIndex(2)  # index of Inventory Sys
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    ##################################################################################
    #####           FUNCTION TO VALIDATE THE LOGIN CREDENTIALS               #########
    ##################################################################################

    def validate_credentials(self, username, password):
        """Validate credentials against the database."""
        try:
            # Connect to the database
            connection = sqlite3.connect("LoginDB.db")
            cursor = connection.cursor()

            # Query the Login table
            query = "SELECT * FROM Login WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            connection.close()

            # Return True if credentials are found
            return result is not None

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            return False