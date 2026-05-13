from PyQt6.QtWidgets import QDialog
import os
from PyQt6.QtGui import QPalette, QBrush, QPixmap
from ui.py_ui.ui_login import Ui_LoginDialog
from client.core.player import Player
from client.network.tcp_client import TCPClient
from PyQt6.QtCore import pyqtSignal, Qt


class LoginWindow(QDialog):

    login_success = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.handle_login)

        self.setup_background()

    def setup_background(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        image_path = os.path.join(base_dir, "..", "assets", "images", "risk_login.jpg")

        if os.path.exists(image_path):
            palette = QPalette()
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
        else:
            print(f"Uyarı: Resim bulunamadı, aranan yol: {image_path}")


    def handle_login(self):

        player_name = self.ui.lineEdit.text().strip()

        if player_name:
            self.player = Player(name=player_name)

            self.client = TCPClient(
                player_name=self.player.name,
                player_char=self.player.character_image
            )

            self.player.client = self.client

            self.login_success.emit(self.player)

            self.close()

    def closeEvent(self, event):
        if hasattr(self, 'player') and self.player.client:
            self.player.client.send_disconnect_message()
            self.player.client.close_connection()

        event.accept()