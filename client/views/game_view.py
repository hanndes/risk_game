import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from client.ui.ui_game_window import Ui_MainWindow
from client.core.player import Player


class GameWindow(QMainWindow):
    def __init__(self, player_obj=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if player_obj:
            self.setWindowTitle(f"Risk - Komutan: {player_obj.name}")
        else:
            self.setWindowTitle("Risk: Dünya Egemenliği")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_player = Player("Komutanı")

    window = GameWindow(test_player)
    window.show()

    sys.exit(app.exec())