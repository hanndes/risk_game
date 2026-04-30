import os
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

from client.utils.map_parser import svg_d_to_qpath


class UIMap(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QColor("#1a1a1a"))

        self.off_x = -167.99651
        self.off_y = -118.55507

        self.regions = {}
        self.load_precise_map()

    def load_precise_map(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.map_path = os.path.join(script_dir, "../assets/images/risk_map.svg")

        if not os.path.exists(self.map_path):
            print(f"HATA: Harita dosyası bulunamadı: {self.map_path}")
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
                        item.setBrush(QBrush(QColor(46, 204, 113, 100)))
                        item.setPos(self.off_x, self.off_y)
                        item.setAcceptHoverEvents(True)
                        item.setToolTip(rid)

                        self.scene.addItem(item)
                        self.regions[rid] = item
                break

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        for r in self.regions.values():
            r.setBrush(QBrush(QColor(46, 204, 113, 100)))

        if isinstance(item, QGraphicsPathItem):
            region_id = [k for k, v in self.regions.items() if v == item][0]
            print(f"\n>>> TIKLANAN ÜLKE: {region_id}")
            item.setBrush(QBrush(QColor(220, 50, 40, 180)))

        super().mousePressEvent(event)

    def wheelEvent(self, event):
        f = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale(f, f)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    win = QMainWindow()
    win.setWindowTitle("Harita Test Modu")
    win.resize(1000, 700)

    map_widget = UIMap()
    win.setCentralWidget(map_widget)

    win.show()
    sys.exit(app.exec())