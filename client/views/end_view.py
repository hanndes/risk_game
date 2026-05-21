from PyQt6.QtWidgets import QWidget
from ui.py_ui.ui_end_window import Ui_EndScreen

class EndWindow(QWidget, Ui_EndScreen):
    def __init__(self, is_winner, player_name):
        super().__init__()
        self.setupUi(self)

        if self.mainLayout:
            self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.playerNameLabel.setText(f"KOMUTAN {player_name.upper()}")

        if is_winner:
            self.resultLabel.setText("KAZANDINIZ")
            self.resultLabel.setProperty("result", "win")
            self.subtitleLabel.setText("DÜNYA EGEMENLİĞİ TAMAMLANDI")
        else:
            self.resultLabel.setText("KAYBETTİNİZ")
            self.resultLabel.setProperty("result", "lose")
            self.subtitleLabel.setText("BİRLİKLERİNİZ YOK EDİLDİ")

        self.resultLabel.style().unpolish(self.resultLabel)
        self.resultLabel.style().polish(self.resultLabel)