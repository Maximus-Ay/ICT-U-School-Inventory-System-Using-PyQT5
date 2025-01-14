from PyQt5 import QtWidgets, uic
import myassets

class InventorySysWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Load the Inventory System UI
        uic.loadUi("InventorySys.ui", self)

    