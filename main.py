from PyQt5 import QtWidgets
import sys
from login import LoginWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()