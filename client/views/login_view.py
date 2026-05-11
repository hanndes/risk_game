from PyQt6.QtWidgets import QDialog

from ui.py_ui.ui_login import Ui_LoginDialog
from client.views.waiting_room_view import WaitingRoomWindow
from client.core.player import Player
from client.network.tcp_client import TCPClient
from PyQt6.QtCore import pyqtSignal

class LoginWindow(QDialog):

    login_success = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.handle_login)

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
