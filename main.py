from PyQt5 import QtWidgets
import sys
from Welcome import WelcomeWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()