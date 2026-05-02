import random
import os
import logging

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QPixmap

from client.ui.ui_waiting_room import Ui_MainWindow as Ui_WaitingRoom

from client.views.game_view import GameWindow
from shared.constants import MessageTypes

from PyQt6.QtCore import pyqtSignal

class WaitingRoomWindow(QMainWindow):

    trigger_game_start = pyqtSignal(str, str)

    def __init__(self, player_obj):
        super().__init__()
        self.ui = Ui_WaitingRoom()
        self.ui.setupUi(self)

        self.player = player_obj

        self.trigger_game_start.connect(self.play_game)

        self.ui.gamer1_name.setText(self.player.name)
        self.ui.gamer2_name.setText("Rakip Aranıyor...")

        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(0)

        self.assign_random_character()

    def update_ui(self, data: dict):
        msg_type = data.get("type")

        if msg_type == "CONN_INFO":

            self.opp_name = data.get("opponent_name")
            self.opp_img_path = f"assets/images/chars/{data.get('opponent_char')}"

            self.ui.gamer2_name.setText(self.opp_name)
            if os.path.exists(self.opp_img_path):
                self.ui.gamer2_icon.setPixmap(QPixmap(self.opp_img_path))
                self.ui.gamer2_icon.setScaledContents(True)

            logging.info(f"Rakip bilgileri alındı: {self.opp_name}")

        elif msg_type == MessageTypes.GAME_START:
            opp_name = getattr(self, 'opp_name', "Rakip")
            opp_path = getattr(self, 'opp_img_path', "assets/images/chars/default.png")
            self.trigger_game_start.emit(opp_name, opp_path)

    def assign_random_character(self):
        chars_path = "assets/images/chars"

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

    def play_game(self, opponent_name, opponent_img_path):
        print(f"Rakip {opponent_name} bulundu, oyuna geçiliyor!")

        player1_img = f"assets/images/chars/{self.player.character_image}"

        self.game_window = GameWindow(
            player_obj=self.player,
            opp_name=opponent_name,
            opp_img=opponent_img_path
        )
        self.game_window.show()
        self.close()