import sys

from PyQt6.QtWidgets import QApplication
from client.views.login_view import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())