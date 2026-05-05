import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from ui.py_ui.ui_game_window import Ui_GameWindow
from core.player import Player
from ui.widgets.map_widget import UIMap


class GameWindow(QMainWindow):
    def __init__(self, player_obj, opp_name, opp_img):
        super().__init__()

        self.ui = Ui_GameWindow()
        self.ui.setupUi(self)

        self.map_widget = UIMap()
        self.ui.map_vbox.addWidget(self.map_widget)

        if player_obj:
            self.setWindowTitle(f"Risk - Komutan: {player_obj.name} vs {opp_name}")
            self.ui.label_player_name.setText(player_obj.name)
            self.ui.label_opponent_name.setText(opp_name)

    def updaite_ui_from_server(self, game_state):
        self.ui.label_player_name.setText(game_state['player_name'])
        self.ui.label_troops_value.setText(str(game_state['troops']))

        self.ui.progress_bar.setValue(game_state['territory_percent'])

        self.ui.label_turn_indicator.setText(game_state['turn_msg'])
        self.ui.label_phase.setText(f"FAZ: {game_state['current_phase']}")

        self.ui.log_box.append(f"• {game_state['last_action']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_player = Player("Komutanı")

    window = GameWindow(test_player)
    window.show()

    sys.exit(app.exec())