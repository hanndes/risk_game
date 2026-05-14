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

        self.app.aboutToQuit.connect(self.shutdown_application)

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
        print(f"!!! AĞDAN BİR VERİ GELDİ: Tipi -> {type(data)}")  # Bunu ekle
        if isinstance(data, dict):
            msg_type = data.get("type")

            if msg_type == "CONN_INFO":
                assigned_id = data.get("assigned_id")
                if assigned_id:
                    self.player.id = assigned_id
                self.opp_name = data.get("opponent_name")
                self.opp_char = data.get("opponent_char")
                if self.waiting_room:
                    self.waiting_room.update_opponent_info(data)

            elif msg_type == "GAME_START":
                self.transition_to_game()

            elif msg_type == "ERROR":
                error_message = data.get("message", "Bilinmeyen bir kural hatası.")
                if self.game_window:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self.game_window, "Komutanım, Dikkat!", error_message)

            elif msg_type == "BATTLE_RESULT":
                if self.game_window:
                    self.game_window.battle_result_signal.emit(data)

            elif msg_type == "OPPONENT_LEFT":
                self.return_to_waiting_room()

        else:
            logging.info("Ağdan GameState objesi yakalandı!")
            self.last_received_state = data

            if self.game_window:
                self.game_window.update_ui_with_state(data)

    def transition_to_game(self):
        logging.info("Oyun başlatılıyor, sahne değişimi yapılıyor.")

        if self.waiting_room:
            self.waiting_room.is_switching_to_game = True

            self.waiting_room.close()

        opp_name = getattr(self, 'opp_name', 'Rakip')
        opp_img = getattr(self, 'opp_char', None)

        self.game_window = GameWindow(self.player, opp_name, opp_img)
        self.game_window.show()

        if hasattr(self, 'last_received_state'):
            self.game_window.update_ui_with_state(self.last_received_state)

    def run(self):
        sys.exit(self.app.exec())

    def return_to_waiting_room(self):
        logging.info("Rakip ayrıldı. Kullanıcıya bilgi verilip uygulama kapatılacak.")

        from PyQt6.QtWidgets import QMessageBox

        active_window = self.game_window if self.game_window else self.waiting_room

        msg_box = QMessageBox(active_window)
        msg_box.setWindowTitle("Bağlantı Koptu")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("Rakibiniz oyundan ayrıldı veya bağlantısı kesildi.")
        msg_box.setInformativeText(
            "Güvenliğiniz için bağlantı sonlandırıldı. Lütfen uygulamayı kapatıp yeniden giriş yapın.")

        kapat_btn = msg_box.addButton("Bağlantıyı Kapat", QMessageBox.ButtonRole.AcceptRole)

        msg_box.exec()

        self.app.quit()

    def shutdown_application(self):
        logging.info("Uygulama kapatılıyor, ağ bağlantısı kesiliyor...")
        if self.player and self.player.client:
            self.player.client.send_disconnect_message()
            self.player.client.close_connection()
