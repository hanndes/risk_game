import random
import os
import logging

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QPixmap

from ui.py_ui.ui_waiting_room import Ui_MainWindow as Ui_WaitingRoom

from PyQt6.QtCore import pyqtSignal

class WaitingRoomWindow(QMainWindow):

    trigger_game_start = pyqtSignal(str, str)


    def __init__(self, player_obj):
        super().__init__()
        self.ui = Ui_WaitingRoom()
        self.ui.setupUi(self)

        self.player = player_obj

        self.ui.gamer1_name.setText(self.player.name)
        self.ui.gamer2_name.setText("Rakip Aranıyor...")
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(0)
        self.is_switching_to_game = False

        self.assign_random_character()


    def update_opponent_info(self, data: dict):
        opp_name = data.get("opponent_name")
        opp_char = data.get("opponent_char")

        self.ui.gamer2_name.setText(opp_name)
        opp_img_path = f"assets/images/chars/{opp_char}"

        if os.path.exists(opp_img_path):
            self.ui.gamer2_icon.setPixmap(QPixmap(opp_img_path))
            self.ui.gamer2_icon.setScaledContents(True)

        logging.info(f"Bekleme Odası: Rakip {opp_name} bilgileri ekrana basıldı.")

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

    def closeEvent(self, event):
        if self.is_switching_to_game:
            logging.info("Oyun ekranına geçiliyor, bağlantı korunuyor.")
            event.accept()
            return

        logging.info("Bekleme odasından çıkılıyor, bağlantı temizleniyor...")

        if hasattr(self, 'player') and self.player and hasattr(self.player, 'client'):
            try:
                self.player.client.send_disconnect_message()
                self.player.client.close_connection()
            except Exception as e:
                logging.error(f"Bekleme odası kapatılırken hata oluştu: {e}")

        event.accept()