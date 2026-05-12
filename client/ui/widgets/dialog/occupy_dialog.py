from PyQt6.QtWidgets import QDialog
from ui.py_ui.ui_occupy_dialog import Ui_OccupyDialog  # Dönüştürdüğün dosyanın adı


class OccupyDialog(QDialog):
    def __init__(self, source_region, target_region, max_transferable, parent=None):
        super().__init__(parent)
        self.ui = Ui_OccupyDialog()
        self.ui.setupUi(self)

        self.max_transferable = max_transferable

        self.ui.infoLabel.setText(f"Tebrikler Komutan!\n{target_region} bölgesini fethettiniz.\n"
                                  f"{source_region} bölgesinden kaç asker aktarmak istersiniz?")

        self.ui.slider.setRange(1, max_transferable)  # En az 1 asker kaydırmak zorunlu olabilir
        self.ui.spinBox.setRange(1, max_transferable)

        self.ui.slider.setValue(max_transferable)
        self.ui.spinBox.setValue(max_transferable)

        self.ui.slider.valueChanged.connect(self.ui.spinBox.setValue)
        self.ui.spinBox.valueChanged.connect(self.ui.slider.setValue)

        self.ui.btnConfirm.clicked.connect(self.accept)

    def get_value(self):
        return self.ui.slider.value()