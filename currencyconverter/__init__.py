import sys

from PyQt6.QtWidgets import QApplication

from .controller import Controller


def main():
    """
    Initiate the application. Create a PyQt6 application and a Controller object.
    """
    app = QApplication(sys.argv)
    c = Controller()
    try:
        c.view.show()
        exit_code = app.exec()
    finally:
        c.close()
    sys.exit(exit_code)
