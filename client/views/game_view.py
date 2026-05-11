import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QMessageBox,
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QSpinBox, QPushButton)
from PyQt6.QtCore import Qt
from ui.py_ui.ui_game_window import Ui_GameWindow
from core.player import Player
from ui.widgets.map_widget import UIMap
from ui.widgets.dialog.troop_selection_dialog import TroopSelectionDialog
import pickle

class GameWindow(QMainWindow):
    def __init__(self, player_obj:Player, opp_name="Bekleniyor...", opp_img=None):
        super().__init__()

        self.player_obj = player_obj

        self.ui = Ui_GameWindow()
        self.ui.setupUi(self)

        self.map_widget = UIMap()
        self.ui.map_vbox.addWidget(self.map_widget)

        self.my_player_id = player_obj.id if hasattr(player_obj, 'id') else "player1"

        if player_obj:
            self.setWindowTitle(f"Risk - Komutan: {player_obj.name} vs {opp_name}")
            self.ui.label_player_name.setText(player_obj.name)
            self.ui.label_opponent_name.setText(opp_name)

        self.ui.btn_reinforce.clicked.connect(self.on_reinforce_clicked)

    def update_ui_with_state(self, state):
        if isinstance(state, dict):
            return

        print(">>> UI GÜNCELLEME TETİKLENDİ: Veriler kutulara yazılıyor...")

        phase_map = {
            "DRAFT": "TAKVİYE",
            "ATTACK": "SALDIRI",
            "FORTIFY": "KUVVETLERİ TAŞI"
        }

        display_phase = phase_map.get(state.phase, state.phase)

        if state.current_player == self.my_player_id:
            self.ui.label_turn_indicator.setText("SENİN TURUN")
            self.ui.label_turn_indicator.setStyleSheet(
                "background-color: #44cc44; color: #ffffff; padding: 3px 10px; border-radius: 3px;")  # Yeşil renk
            self.ui.label_phase.setText(f"FAZ: {display_phase}")

            self.ui.btn_reinforce.setEnabled(state.phase == "DRAFT")
            self.ui.btn_attack.setEnabled(state.phase == "ATTACK")
            self.ui.btn_fortify.setEnabled(state.phase == "FORTIFY")
            self.ui.btn_end_turn.setEnabled(True)
        else:
            self.ui.label_turn_indicator.setText("RAKİBİN TURU")
            self.ui.label_turn_indicator.setStyleSheet(
                "background-color: #8b1a1a; color: #ffffff; padding: 3px 10px; border-radius: 3px;")  # Kırmızı renk
            self.ui.label_phase.setText(f"Sıradaki: {display_phase}")

            self.ui.btn_reinforce.setEnabled(False)
            self.ui.btn_attack.setEnabled(False)
            self.ui.btn_fortify.setEnabled(False)
            self.ui.btn_end_turn.setEnabled(False)

        my_region_count = 0
        opp_region_count = 0
        total_regions = len(state.regions) if len(state.regions) > 0 else 42

        for region_id, region_data in state.regions.items():
            owner = region_data["owner"]
            troops = region_data["troops"]

            if owner == self.my_player_id:
                my_region_count += 1
                display_owner = "player1"
            else:
                opp_region_count += 1
                display_owner = "player2"

            if hasattr(self.map_widget, 'update_region_ui'):
                self.map_widget.update_region_ui(region_id, display_owner, troops)

        self.ui.label_territories_value.setText(f"{my_region_count} / {total_regions}")
        self.ui.label_opponent_territories_value.setText(f"{opp_region_count} / {total_regions}")

        if total_regions > 0:
            percentage = int((my_region_count / total_regions) * 100)
            self.ui.progress_bar.setValue(percentage)

        if hasattr(state, "turn"):
            self.ui.label_round_value.setText(str(state.turn))

        if hasattr(state, "last_log") and state.last_log:
            self.ui.log_box.append(f"Karargah: {state.last_log}")

        my_leftover = state.unplaced_troops.get(self.my_player_id, 0)
        self.ui.label_troops_value.setText(str(my_leftover))

        opp_id = "player2" if self.my_player_id == "player1" else "player1"
        opp_leftover = state.unplaced_troops.get(opp_id, 0)
        self.ui.label_opponent_troops_value.setText(str(opp_leftover))

    def on_reinforce_clicked(self):

        if not hasattr(self.map_widget, 'on_region_clicked'):
            QMessageBox.critical(self, "Hata", "Lütfen harita üzerinde bir bölge seçiniz!")
            return

        selected_region = getattr(self.map_widget, 'selected_region', None)

        if not selected_region:
            QMessageBox.warning(self, "Komutanım!", "Lütfen haritadan takviye göndermek istediğiniz bölgeyi seçin.")
            return

        my_leftover = int(self.ui.label_troops_value.text())
        if my_leftover <= 0:
            QMessageBox.information(self, "Bilgi", "Gönderilecek yedek askeriniz kalmadı.")
            return

        dialog = TroopSelectionDialog(selected_region, my_leftover, self)

        if dialog.exec():
            amount = dialog.get_value()

            action_data = {
                "action": "DRAFT",
                "region": selected_region,
                "amount": amount
            }

            print(f">>> Sunucuya İstek Paketleniyor: {action_data}")

            try:
                if self.player_obj:
                    self.player_obj.send_action(action_data)
                else:
                    print("HATA: Player objesi bulunamadı!")
            except Exception as e:
                QMessageBox.critical(self, "Bağlantı Hatası", f"Sunucuya veri gönderilirken hata oluştu:\n{e}")

            print(f">>> Sunucuya İstek: {action_data}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_player = Player("Komutanı")

    window = GameWindow(test_player, opp_name="Komutan Hande")
    window.show()

    sys.exit(app.exec())