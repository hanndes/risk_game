from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QSpinBox, QPushButton)
from PyQt6.QtCore import Qt


class TroopSelectionDialog(QDialog):
    def __init__(self, region_name, max_troops, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Takviye Gönder")
        self.setMinimumWidth(320)

        self.setStyleSheet("background-color: #1f0800; color: #e8c090; font-family: 'Andale Mono';")

        self.layout = QVBoxLayout(self)

        self.info_label = QLabel(f"{region_name} bölgesine takviye edilecek\nasker miktarını seçin:", self)
        self.layout.addWidget(self.info_label)

        self.control_layout = QHBoxLayout()

        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setMinimum(1)
        self.slider.setMaximum(max_troops)
        self.slider.setValue(1)

        self.slider.setStyleSheet(
            "QSlider::handle:horizontal { background: #8b1a1a; width: 15px; border-radius: 3px; }")

        self.spinbox = QSpinBox(self)
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(max_troops)
        self.spinbox.setValue(1)
        self.spinbox.setStyleSheet(
            "background-color: #0d0500; color: #ff6644; font-size: 14px; font-weight: bold; border: 1px solid #4a1a0a;")

        self.slider.valueChanged.connect(self.spinbox.setValue)
        self.spinbox.valueChanged.connect(self.slider.setValue)

        self.control_layout.addWidget(self.slider)
        self.control_layout.addWidget(self.spinbox)
        self.layout.addLayout(self.control_layout)

        self.button_layout = QHBoxLayout()

        self.btn_ok = QPushButton("ONAYLA", self)
        self.btn_ok.setStyleSheet(
            "background-color: #3a1500; color: #ffcc88; font-weight: bold; padding: 6px; border: 1px solid #8b4010; border-radius: 4px;")

        self.btn_cancel = QPushButton("İPTAL", self)
        self.btn_cancel.setStyleSheet(
            "background-color: #1a1a0a; color: #888888; padding: 6px; border: 1px solid #4a1a0a; border-radius: 4px;")

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        self.button_layout.addWidget(self.btn_ok)
        self.button_layout.addWidget(self.btn_cancel)
        self.layout.addLayout(self.button_layout)

    def get_value(self):
        return self.spinbox.value()