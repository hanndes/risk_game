import logging
import os
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt
from PyQt6.uic.properties import QtGui

from shared.constants import REGION_NEIGHBORS
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsTextItem

from client.utils.map_parser import svg_d_to_qpath


class UIMap(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QColor("#0084CF"))

        self.off_x = -167.99651
        self.off_y = -118.55507

        self.regions = {}
        self.load_precise_map()

        if self.scene.items():
            self.scene.setSceneRect(self.scene.itemsBoundingRect())

        self.regions = {}
        self.troop_texts = {}
        self.load_precise_map()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def load_precise_map(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.map_path = os.path.join(script_dir, "../../assets/images/risk_map.svg")

        if not os.path.exists(self.map_path):
            logging.error(f"HATA: Harita dosyası bulunamadı: {self.map_path}")
            return

        tree = ET.parse(self.map_path)
        root = tree.getroot()
        ns = {'svg': 'http://www.w3.org/2000/svg',
              'inkscape': 'http://www.inkscape.org/namespaces/inkscape'}

        for group in root.findall('.//svg:g', ns):
            if group.get('{http://www.inkscape.org/namespaces/inkscape}label') == "countries":
                for path_data in group.findall('.//svg:path', ns):
                    rid = path_data.get("id")
                    d_attr = path_data.get("d")

                    if rid and d_attr:
                        qpath = svg_d_to_qpath(d_attr)
                        item = QGraphicsPathItem(qpath)

                        item.setPen(QPen(QColor(255, 255, 255, 50), 1))
                        item.setBrush(QBrush(QColor(25, 91, 0, 100)))
                        item.setPos(self.off_x, self.off_y)
                        item.setAcceptHoverEvents(True)
                        item.setToolTip(rid)

                        self.scene.addItem(item)
                        self.regions[rid] = item
                break

    def update_region_ui(self, region_id, owner, troops):
        if region_id not in self.regions:
            logging.warning(f"Bölge bulunamadı: {region_id}")
            return

        item = self.regions[region_id]

        if owner == "player1":
            color = QColor(0, 0, 200, 150)
        elif owner == "player2":
            color = QColor(200, 0, 0, 150)
        else:
            color = QColor(25, 91, 0, 100)

        item.base_color = color

        # Eğer bölge o an seçiliyse beyaz kalsın, değilse kendi rengiyle boyansın
        if getattr(self, 'selected_region', None) == region_id:
            item.setBrush(QBrush(QColor(255, 255, 255, 200)))
        else:
            item.setBrush(QBrush(color))

        if region_id not in self.troop_texts:
            text_item = QGraphicsTextItem(str(troops))
            text_item.setDefaultTextColor(Qt.GlobalColor.white)

            font = text_item.font()
            font.setBold(True)
            font.setPointSize(12)
            text_item.setFont(font)

            self.scene.addItem(text_item)
            self.troop_texts[region_id] = text_item

            center = item.sceneBoundingRect().center()
            text_item.setPos(
                center.x() - text_item.boundingRect().width() / 2,
                center.y() - text_item.boundingRect().height() / 2
            )
        else:
            self.troop_texts[region_id].setPlainText(str(troops))

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())

        for r in self.regions.values():
            if hasattr(r, 'base_color'):
                r.setBrush(QBrush(r.base_color))
            else:
                r.setBrush(QBrush(QColor(25, 91, 0, 100)))

        if isinstance(item, QGraphicsPathItem):
            region_id = [k for k, v in self.regions.items() if v == item][0]
            logging.info(f"\n>>> SEÇİLEN BÖLGE: {region_id}")

            self.selected_region = region_id

            item.setBrush(QBrush(QColor(255, 255, 255, 200)))

        else:
            self.selected_region = None

        super().mousePressEvent(event)

    def wheelEvent(self, event):
        f = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale(f, f)

    def on_region_clicked(self, region_id):

        if region_id not in REGION_NEIGHBORS:
            return

        neighbors = REGION_NEIGHBORS.get(region_id, [])

        focus_list = neighbors + [region_id]

        for current_region_id, path_item in self.region_items.items():
            if current_region_id in focus_list:
                path_item.setOpacity(1.0)
                path_item.setPen(QtGui.QPen(QtGui.QColor("white"), 2))
            else:
                path_item.setOpacity(0.3)
                path_item.setPen(QtGui.QPen(QtGui.QColor("black"), 1))

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    win = QMainWindow()
    win.setWindowTitle("Sadece Harita")
    win.resize(1000, 700)

    map_widget = UIMap()
    win.setCentralWidget(map_widget)

    win.show()
    sys.exit(app.exec())