import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from ui.py_ui.ui_game_window import Ui_GameWindow
from core.player import Player
from ui.widgets.map_widget import UIMap

class GameWindow(QMainWindow):
    def __init__(self, player_obj:Player, opp_name="Bekleniyor...", opp_img=None):
        super().__init__()

        self.ui = Ui_GameWindow()
        self.ui.setupUi(self)

        self.map_widget = UIMap()
        self.ui.map_vbox.addWidget(self.map_widget)

        self.my_player_id = player_obj.id if hasattr(player_obj, 'id') else "player1"

        if player_obj:
            self.setWindowTitle(f"Risk - Komutan: {player_obj.name} vs {opp_name}")
            self.ui.label_player_name.setText(player_obj.name)
            self.ui.label_opponent_name.setText(opp_name)

    def update_ui_with_state(self, state):
        if isinstance(state, dict):
            return

        print(">>> UI GÜNCELLEME TETİKLENDİ: Veriler kutulara yazılıyor...")

        if state.current_player == self.my_player_id:
            self.ui.label_turn_indicator.setText("SENİN TURUN")
            self.ui.label_phase.setText(f"FAZ: {state.phase}")

            self.ui.btn_attack.setEnabled(True)
            self.ui.btn_end_turn.setEnabled(True)
        else:
            self.ui.label_turn_indicator.setText("RAKİBİN TURU")
            self.ui.label_phase.setText("BEKLENİYOR...")

            self.ui.btn_attack.setEnabled(False)
            self.ui.btn_end_turn.setEnabled(False)

        for region_id, region_data in state.regions.items():
            owner = region_data["owner"]
            troops = region_data["troops"]

            if hasattr(self.map_widget, 'update_region_ui'):
                self.map_widget.update_region_ui(region_id, owner, troops)

        if hasattr(state, "last_log") and state.last_log:
            self.ui.log_box.append(f"Karargah: {state.last_log}")

        my_leftover = state.unplaced_troops.get(self.my_player_id, 0)
        self.ui.label_troops_value.setText(str(my_leftover))

        opp_id = "player2" if self.my_player_id == "player1" else "player1"
        opp_leftover = state.unplaced_troops.get(opp_id, 0)
        self.ui.label_opponent_troops_value.setText(str(opp_leftover))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_player = Player("Komutanı")

    window = GameWindow(test_player, opp_name="Komutan Hande")
    window.show()

    sys.exit(app.exec())