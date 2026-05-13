import logging
import os
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsTextItem
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt

from shared.constants import REGION_NEIGHBORS
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
            r.setOpacity(1.0)
            r.setPen(QPen(QColor(255, 255, 255, 50), 1))
            if hasattr(r, 'base_color'):
                r.setBrush(QBrush(r.base_color))
            else:
                r.setBrush(QBrush(QColor(25, 91, 0, 100)))

        if isinstance(item, QGraphicsPathItem):
            region_id = [k for k, v in self.regions.items() if v == item][0]
            logging.info(f"\n>>> TIKLANAN BÖLGE: {region_id}")

            window = self.window()

            if hasattr(window, 'current_state') and getattr(window, 'current_state', None):
                state = window.current_state
                my_id = window.my_player_id
                phase = state.phase

                # Eğer tıklanan bölge BENİMSE
                if state.regions[region_id]["owner"] == my_id:
                    # SALDIRI VE TAKVİYE FAZI:
                    if phase == "ATTACK" or phase == "DRAFT":
                        self.selected_region = region_id
                        self.target_region = None
                        item.setBrush(QBrush(QColor(255, 255, 255, 200)))  # Kaynak beyazı

                        if phase == "ATTACK":
                            self.highlight_enemy_neighbors(region_id, state, my_id)

                    # KUVVETLERİ TAŞI FAZI
                    elif phase == "FORTIFY":
                        if not getattr(self, 'selected_region', None) or (
                                self.selected_region and self.target_region):
                            self.selected_region = region_id
                            self.target_region = None
                            item.setBrush(QBrush(QColor(255, 255, 255, 200)))
                            self.highlight_friendly_reachable(region_id, state, my_id)
                        # İPTAL DURUMU
                        elif self.selected_region == region_id:
                            self.clear_selection()
                        # İKİNCİ TIKLAMA
                        else:
                            reachable = self.get_reachable_territories(self.selected_region, state, my_id)
                            if region_id in reachable:
                                self.target_region = region_id
                                logging.info(f">>> HEDEF SEÇİLDİ (TAHKİMAT): {region_id}")

                                self.regions[self.selected_region].setBrush(QBrush(QColor(255, 255, 255, 200)))
                                item.setBrush(QBrush(QColor(0, 255, 255, 180)))
                                self.highlight_friendly_reachable(self.selected_region, state, my_id)
                            else:
                                # Ulaşılamayan kendi bölgesine tıkladıysa, orayı "Yeni Kaynak" yap
                                self.selected_region = region_id
                                self.target_region = None
                                item.setBrush(QBrush(QColor(255, 255, 255, 200)))
                                self.highlight_friendly_reachable(region_id, state, my_id)

                # Eğer tıklanan bölge RAKİBİNSE
                elif phase == "ATTACK" and getattr(self, 'selected_region', None):
                    neighbors = REGION_NEIGHBORS.get(self.selected_region, [])
                    if region_id in neighbors:
                        self.target_region = region_id
                        logging.info(f">>> HEDEF SEÇİLDİ: {region_id}")

                        self.regions[self.selected_region].setBrush(QBrush(QColor(255, 255, 255, 200)))

                        item.setBrush(QBrush(QColor(255, 255, 0, 180)))
                        self.highlight_enemy_neighbors(self.selected_region, state, my_id)
            else:
                self.selected_region = region_id
                item.setBrush(QBrush(QColor(255, 255, 255, 200)))

        else:
            self.selected_region = None
            self.target_region = None

        super().mousePressEvent(event)

    def highlight_enemy_neighbors(self, region_id, state, my_id):
        neighbors = REGION_NEIGHBORS.get(region_id, [])

        for r_id, item in self.regions.items():
            item.setOpacity(0.4)

        self.regions[region_id].setOpacity(1.0)

        for n in neighbors:
            if state.regions[n]["owner"] != my_id:
                enemy_item = self.regions[n]
                enemy_item.setOpacity(1.0)
                enemy_item.setPen(QPen(QColor("white"), 3))

    def clear_selection(self):

        self.selected_region = None
        self.target_region = None

        for r in self.regions.values():
            r.setOpacity(1.0)
            r.setPen(QPen(QColor(255, 255, 255, 50), 1))

            if hasattr(r, 'base_color'):
                r.setBrush(QBrush(r.base_color))
            else:
                r.setBrush(QBrush(QColor(25, 91, 0, 100)))

        self.update()

    def get_reachable_territories(self, start_region, state, my_id):

        reachable = []
        visited = set()
        queue = [start_region]
        visited.add(start_region)

        while queue:
            current = queue.pop(0)
            neighbors = REGION_NEIGHBORS.get(current, [])

            for neighbor in neighbors:
                if neighbor not in visited and state.regions[neighbor]["owner"] == my_id:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    reachable.append(neighbor)

        return reachable

    def highlight_friendly_reachable(self, region_id, state, my_id):
        reachable = self.get_reachable_territories(region_id, state, my_id)

        for r_id, item in self.regions.items():
            item.setOpacity(0.4)

        self.regions[region_id].setOpacity(1.0)

        for n in reachable:
            friendly_item = self.regions[n]
            friendly_item.setOpacity(1.0)
            friendly_item.setPen(QPen(QColor(0, 255, 255, 200), 3))

    def wheelEvent(self, event):
        f = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale(f, f)
