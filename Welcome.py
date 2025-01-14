from PyQt5 import QtWidgets, uic
import myassets

class WelcomeWindow(QtWidgets.QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        # Load the Welcome UI
        uic.loadUi("Welcome.ui", self)
        self.stacked_widget = stacked_widget

        # Connect the button to switch to the Login page
        self.welcome_btn.clicked.connect(self.go_to_login)

        
    ##################################################################
    ### FUNCTION TO GO TO THE LOGIN PAGE FROM THE WELCOME PAGE    ####
    ##################################################################
    def go_to_login(self):
        """Switch to the Login page."""
        self.stacked_widget.setCurrentIndex(1)  # Index of Login page