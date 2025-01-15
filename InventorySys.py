from PyQt5 import QtWidgets, uic
import Images

class InventorySysWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Load the Inventory System UI
        uic.loadUi("InventorySys.ui", self)

        # Connect buttons to their respective functions
        self.DashboardBtn.clicked.connect(self.show_dashboard)
        self.ModifyItemsBtn.clicked.connect(self.show_modify_items)
        self.SignInSignOutBtn.clicked.connect(self.show_sign_in_sign_out)
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

    


