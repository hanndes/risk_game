from PyQt6.QtWidgets import QDialog
from ui.py_ui.ui_troop_selection_dialog import Ui_TroopSelectionDialog


class TroopSelectionDialog(QDialog):
    def __init__(self, region_name, max_troops, parent=None):
        super().__init__(parent)
        self.ui = Ui_TroopSelectionDialog()
        self.ui.setupUi(self)

        self.ui.info_label.setText(
            f"{region_name} bölgesine takviye edilecek\nasker miktarını seçin:"
        )

        self.ui.slider.setRange(1, max_troops)
        self.ui.spinbox.setRange(1, max_troops)

        self.ui.slider.setValue(1)
        self.ui.spinbox.setValue(1)

        self.ui.slider.valueChanged.connect(self.ui.spinbox.setValue)
        self.ui.spinbox.valueChanged.connect(self.ui.slider.setValue)

        self.ui.btn_ok.clicked.connect(self.accept)
        self.ui.btn_cancel.clicked.connect(self.reject)

    def get_value(self):
        return self.ui.spinbox.value()