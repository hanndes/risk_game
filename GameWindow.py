from ui_game_window import Ui_GameWindow
from game_map import GameMapView  # promote için import şart

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_GameWindow()
        self.ui.setupUi(self)