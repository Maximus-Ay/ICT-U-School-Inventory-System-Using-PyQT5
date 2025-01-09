from PyQt5 import QtWidgets, uic
import sys

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi("Login.ui", self)