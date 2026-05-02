from PyQt6.QtWidgets import QDialog

from client.ui.ui_login import Ui_LoginDialog
from client.views.waiting_room_view import WaitingRoomWindow
from client.core.player import Player
from client.network.tcp_client import TCPClient

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.handle_login)

    def handle_login(self):

        player_name = self.ui.lineEdit.text().strip()

        if player_name:
            self.player = Player(player_name)

            self.waiting_room = WaitingRoomWindow(self.player)

            self.client = TCPClient(
                player_name=self.player.name,
                player_char=self.player.character_image,
                on_message_received_callback=self.waiting_room.update_ui
            )

            self.player.client = self.client

            self.waiting_room.show()
            self.close()
