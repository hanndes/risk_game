import sys
import logging
from PyQt6.QtWidgets import QApplication
from views.login_view import LoginWindow
from views.waiting_room_view import WaitingRoomWindow
from views.game_view import GameWindow


class ClientController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.player = None
        self.waiting_room = None
        self.game_window = None

        # Uygulamayı Login ekranı ile başlat
        self.show_login()

    def show_login(self):
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.start_waiting_session)
        self.login_window.show()

    def start_waiting_session(self, player_obj):
        self.player = player_obj
        self.login_window.close()

        self.waiting_room = WaitingRoomWindow(self.player)

        # pencereyi göstermeden önce sinyali bağla
        self.player.client.signals.state_updated.connect(self.handle_central_messages)

        self.waiting_room.show()

    def handle_central_messages(self, data):
        if isinstance(data, dict):
            msg_type = data.get("type")
            if msg_type == "CONN_INFO":
                self.opp_name = data.get("opponent_name")
                self.opp_char = data.get("opponent_char")
                if self.waiting_room:
                    self.waiting_room.update_opponent_info(data)
            elif msg_type == "GAME_START":
                self.transition_to_game()

        else:
            logging.info("Ağdan GameState objesi yakalandı!")
            # Eğer oyun penceresi henüz açılmadıysa bu objeyi yedekle
            self.last_received_state = data

            # Eğer oyun penceresi zaten açıksa, veriyi ona gönder
            if self.game_window:
                self.game_window.update_ui_with_state(data)

    def transition_to_game(self):
        logging.info("Oyun başlatılıyor, sahne değişimi yapılıyor.")
        if self.waiting_room:
            self.waiting_room.close()

        opp_name = getattr(self, 'opp_name', 'Rakip')
        opp_img = getattr(self, 'opp_char', None)

        self.game_window = GameWindow(self.player, opp_name, opp_img)

        self.game_window.show()

        if hasattr(self, 'last_received_state'):
            print(">>> ELDEKİ VERİ OYUN EKRANINA AKTARILIYOR...")
            self.game_window.update_ui_with_state(self.last_received_state)

    def run(self):
        sys.exit(self.app.exec())
