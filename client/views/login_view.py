from PyQt6.QtWidgets import QDialog

from client.ui.ui_login import Ui_LoginDialog
from client.views.waiting_room_view import WaitingRoomWindow
from client.core.player import Player
from network.tcp_client import TCPClient

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self.client = TCPClient()
        self.ui.pushButton.clicked.connect(self.login_ol_ve_ilerle)

    def login_ol_ve_ilerle(self):
        gelen_isim = self.ui.lineEdit.text().strip()

        if gelen_isim:
            self.user = Player(gelen_isim,self.client)

            self.waiting_room = WaitingRoomWindow(self.user)
            self.waiting_room.show()

            self.close()
        else:
            self.ui.lineEdit.setPlaceholderText("İsim yazmalısınız!")
