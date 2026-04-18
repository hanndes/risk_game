import sys
import random
import os

from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt6.QtGui import QPixmap

from ui_login import Ui_LoginDialog
from ui_waiting_room import Ui_MainWindow as Ui_WaitingRoom
from Player import Player


class WaitingRoomWindow(QMainWindow):
    def __init__(self, player_obj):
        super().__init__()
        self.ui = Ui_WaitingRoom()
        self.ui.setupUi(self)
        self.player = player_obj

        self.ui.gamer1_name.setText(self.player.name)
        self.ui.gamer2_name.setText("Rakip Aranıyor...")

        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(0)

        self.assign_random_character()

    def assign_random_character(self):
        chars_path = "./images/chars"

        try:
            char_files = [f for f in os.listdir(chars_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

            if char_files:
                chosen_char = random.choice(char_files)
                full_path = os.path.join(chars_path, chosen_char)

                pixmap = QPixmap(full_path)
                self.ui.gamer1_icon.setPixmap(pixmap)
                self.ui.gamer1_icon.setScaledContents(True)

                self.player.character_image = chosen_char

                print(f"--- Kayıt Başarılı ---")
                print(f"General: {self.player.name}")
                print(f"Karakter: {self.player.character_image}")
            else:
                print(f"HATA: '{chars_path}' içinde resim yok.")

        except FileNotFoundError:
            print(f"HATA: Klasör yolu bulunamadı: {chars_path}")


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.login_ol_ve_ilerle)

    def login_ol_ve_ilerle(self):
        gelen_isim = self.ui.lineEdit.text().strip()

        if gelen_isim:
            self.user = Player(gelen_isim)

            self.waiting_room = WaitingRoomWindow(self.user)
            self.waiting_room.show()

            self.close()
        else:
            self.ui.lineEdit.setPlaceholderText("İsim yazmalısınız!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())