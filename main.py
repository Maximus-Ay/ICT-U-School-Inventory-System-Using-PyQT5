from PyQt5 import QtWidgets
import sys
from Welcome import WelcomeWindow
from Login import LoginWindow
from InventorySys import InventorySysWindow

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Create the QStackedWidget
    stacked_widget = QtWidgets.QStackedWidget()

    # Create instances of the pages
    welcome_page = WelcomeWindow(stacked_widget)
    login_page = LoginWindow(stacked_widget)
    inventory_page = InventorySysWindow()

    # Add pages to the stacked widget
    stacked_widget.addWidget(welcome_page)  # Index 0
    stacked_widget.addWidget(login_page)   # Index 1
    stacked_widget.addWidget(inventory_page)  # Index 2


    # Set the initial page to the Welcome page
    stacked_widget.setCurrentIndex(0)

    #Setting the dimensions of the stackedwidgets
    stacked_widget.setFixedHeight(743)
    stacked_widget.setFixedWidth(1029)

    # Show the stacked widget
    stacked_widget.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()