import random
import os

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QPixmap

from client.ui.ui_waiting_room import Ui_MainWindow as Ui_WaitingRoom

from client.views.game_view import GameWindow

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
        chars_path = "client/assets/images/chars"

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

    def oyuna_gec(self):
        print("Rakip bulundu, oyuna geçiliyor!")
        player1_img = f"assets/images/chars/{self.player.character_image}"
        player2_img = "assets/images/chars/default_rakip.png"

        self.game_window = GameWindow(
            player_names=(self.player.name, "Gizemli Rakip"),
            image_paths=(player1_img, player2_img)
        )
        self.game_window.show()
        self.close()