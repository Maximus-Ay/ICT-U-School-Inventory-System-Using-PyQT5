from PyQt5 import QtWidgets, uic
import sys

class WelcomeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi("Welcome.ui", self)