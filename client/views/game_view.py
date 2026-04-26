# Asıl oyun ekranı mantığı (Haritaya tıklama, asker yerleştirme)

from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsLineItem, QGraphicsRectItem,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import (
    QPolygonF, QColor, QPen, QBrush, QFont, QPainter,
    QRadialGradient, QLinearGradient, QPixmap
)
from PyQt6.QtCore import Qt, QPointF

from client.ui.ui_game_window import Ui_GameWindow

from client.core.map_data import (
    TERRITORIES, CONNECTIONS, PALETTE, OCEAN_DEEP, OCEAN_MID,
    BORDER_DARK, BORDER_SEL, CONN_COLOR, CONTINENT_LABELS
)

OCEAN_DEEP_COLOR = QColor(*OCEAN_DEEP)
OCEAN_MID_COLOR  = QColor(*OCEAN_MID)
BORDER_DARK_PEN  = QColor(*BORDER_DARK)
BORDER_SEL_PEN   = QColor(*BORDER_SEL)
# Eğer CONN_COLOR (180, 220, 255, 60) gibi 4 değer içeriyorsa (RGBA):
CONN_PEN_COLOR   = QColor(*CONN_COLOR)


# Haritadaki her bir ülkeyi çizen ve üzerine tıklandığında renk değiştirmesini sağlayan sınıf

# ─────────────────────────────────────────────────────
#  TERRITORY ITEM
# ─────────────────────────────────────────────────────
class TerritoryItem(QGraphicsPolygonItem):
    def __init__(self, data, scene_ref):
        pts = [QPointF(x, y) for x, y in data["poly"]]
        super().__init__(QPolygonF(pts))

        self.data   = data
        self.scene_ref = scene_ref

        pal = PALETTE[data["continent"]]
        self.base_color = QColor(*pal["base"])
        self.light_color = QColor(*pal["light"])
        self.dark_color = QColor(*pal["dark"])

        self.selected = False
        self._apply_normal()
        self.setAcceptHoverEvents(True)
        self.setToolTip(data["label"])

    def _apply_normal(self):
        r = self.boundingRect()
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, self.light_color)
        grad.setColorAt(1.0, self.dark_color)
        self.setBrush(QBrush(grad))
        self.setPen(QPen(BORDER_DARK, 1.8))

    def _apply_hover(self):
        self.setBrush(QBrush(self.light_color))
        self.setPen(QPen(QColor(255, 255, 200), 2.0))

    def _apply_selected(self):
        self.setBrush(QBrush(QColor(255, 240, 80, 200)))
        self.setPen(QPen(BORDER_SEL, 2.5))

    def hoverEnterEvent(self, e):
        if not self.selected:
            self._apply_hover()
        super().hoverEnterEvent(e)

    def hoverLeaveEvent(self, e):
        if not self.selected:
            self._apply_normal()
        super().hoverLeaveEvent(e)

    def mousePressEvent(self, e):
        for item in self.scene_ref.territory_items.values():
            if item is not self and item.selected:
                item.selected = False
                item._apply_normal()
        self.selected = not self.selected
        self._apply_selected() if self.selected else self._apply_normal()
        super().mousePressEvent(e)

# okyanusu çizen, ülkeleri yerleştiren ve mouse tekerleğiyle yakınlaştırma (zoom) yapmayı sağlayan sınıflar

# ─────────────────────────────────────────────────────
#  SCENE
# ─────────────────────────────────────────────────────
class GameMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 1000, 590)
        self.territory_items = {}
        self._draw_ocean()
        self._draw_grid()
        self._draw_connections()
        self._draw_territories()
        self._draw_continent_labels()
        self._draw_tokens()

    # ── ocean ──
    def _draw_ocean(self):
        base = QGraphicsRectItem(0, 0, 1000, 590)
        base.setBrush(QBrush(QColor(8, 22, 55)))
        base.setPen(QPen(Qt.PenStyle.NoPen))
        base.setZValue(-3)
        self.addItem(base)

        grad = QRadialGradient(500, 295, 480)
        grad.setColorAt(0.0, QColor(35, 85, 155))
        grad.setColorAt(0.55, QColor(20, 58, 115))
        grad.setColorAt(1.0,  QColor(8, 22, 55))
        bg = QGraphicsRectItem(0, 0, 1000, 590)
        bg.setBrush(QBrush(grad))
        bg.setPen(QPen(Qt.PenStyle.NoPen))
        bg.setZValue(-2)
        self.addItem(bg)

        glow = QRadialGradient(500, 295, 260)
        glow.setColorAt(0.0, QColor(180, 215, 255, 55))
        glow.setColorAt(0.45, QColor(120, 175, 240, 22))
        glow.setColorAt(1.0,  QColor(0, 0, 0, 0))
        glow_item = QGraphicsEllipseItem(140, 75, 720, 440)
        glow_item.setBrush(QBrush(glow))
        glow_item.setPen(QPen(Qt.PenStyle.NoPen))
        glow_item.setZValue(-1)
        self.addItem(glow_item)

    # ── lat/lon grid ──
    def _draw_grid(self):
        lat_pen = QPen(QColor(100, 160, 230, 22), 0.7)
        lon_pen = QPen(QColor(100, 160, 230, 18), 0.7)
        eq_pen  = QPen(QColor(100, 180, 255, 45), 1.0)
        pm_pen  = QPen(QColor(100, 180, 255, 38), 1.0)

        for i, x in enumerate(range(0, 1001, 83)):
            pen = pm_pen if i == 6 else lon_pen
            l = QGraphicsLineItem(x, 0, x, 590)
            l.setPen(pen); l.setZValue(-1); self.addItem(l)

        for i, y in enumerate(range(0, 591, 120)):
            pen = eq_pen if i == 2 else lat_pen
            l = QGraphicsLineItem(0, y, 1000, y)
            l.setPen(pen); l.setZValue(-1); self.addItem(l)

    # ── connection lines ──
    def _draw_connections(self):
        id2t = {t["id"]: t for t in TERRITORIES}
        pen  = QPen(CONN_COLOR, 1.2, Qt.PenStyle.DashLine)
        pen.setDashPattern([4, 5])
        for a_id, b_id in CONNECTIONS:
            ax, ay = id2t[a_id]["tp"]
            bx, by = id2t[b_id]["tp"]
            line = QGraphicsLineItem(ax, ay, bx, by)
            line.setPen(pen); line.setZValue(0)
            self.addItem(line)
            # dot endpoints
            for cx, cy in [(ax, ay), (bx, by)]:
                dot = QGraphicsEllipseItem(cx-2, cy-2, 4, 4)
                dot.setBrush(QBrush(QColor(180, 220, 255, 80)))
                dot.setPen(QPen(Qt.PenStyle.NoPen))
                dot.setZValue(1)
                self.addItem(dot)

    # ── territory polygons ──
    def _draw_territories(self):
        for t in TERRITORIES:
            item = TerritoryItem(t, self)
            item.setZValue(2)
            self.addItem(item)
            self.territory_items[t["id"]] = item

    # ── continent watermark labels ──
    def _draw_continent_labels(self):
        for cl in CONTINENT_LABELS:
            pal  = PALETTE[cl["continent"]]
            txt  = QGraphicsTextItem(cl["text"])
            font = QFont("Georgia", 9, QFont.Weight.Bold)
            txt.setFont(font)
            txt.setDefaultTextColor(QColor(
                pal["light"].red(), pal["light"].green(), pal["light"].blue(), 35))
            txt.setPos(cl["x"], cl["y"])
            txt.setZValue(1)
            self.addItem(txt)

    # ── troop tokens ──
    def _draw_tokens(self):
        for t in TERRITORIES:
            tx, ty = t["tp"]
            troops = t["troops"]
            r = 13

            # outer glow ring
            glow = QGraphicsEllipseItem(tx-r-2, ty-r-2, (r+2)*2, (r+2)*2)
            glow.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            glow.setPen(QPen(QColor(255, 255, 200, 55), 1.5))
            glow.setZValue(4)
            self.addItem(glow)

            # token circle with gradient
            grad = QRadialGradient(tx-3, ty-3, r*1.4)
            grad.setColorAt(0.0, QColor(55, 45, 35))
            grad.setColorAt(1.0, QColor(15, 10, 8))
            circle = QGraphicsEllipseItem(tx-r, ty-r, r*2, r*2)
            circle.setBrush(QBrush(grad))
            circle.setPen(QPen(QColor(210, 185, 130), 1.5))
            circle.setZValue(5)
            self.addItem(circle)

            # troop number
            num = QGraphicsTextItem(str(troops))
            font = QFont("Georgia", 9, QFont.Weight.Bold)
            num.setFont(font)
            num.setDefaultTextColor(QColor(255, 240, 200))
            nw = num.boundingRect().width()
            nh = num.boundingRect().height()
            num.setPos(tx - nw/2, ty - nh/2)
            num.setZValue(6)
            self.addItem(num)

# ─────────────────────────────────────────────────────
#  VIEW
# ─────────────────────────────────────────────────────
class GameMapView(QGraphicsView):
    def __init__(self, parent=None):
        self.scene_map = GameMapScene()
        super().__init__(self.scene_map, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("border: none; background: transparent;")

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 0.87
        self.scale(factor, factor)

    def set_territory_owner(self, tid: str, color: QColor):
        item = self.scene_map.territory_items.get(tid)
        if item:
            item.base_color  = color
            item.light_color = color.lighter(130)
            item.dark_color  = color.darker(140)
            item._apply_normal()

    def set_territory_troops(self, tid: str, count: int):
        for t in TERRITORIES:
            if t["id"] == tid:
                t["troops"] = count
        self.scene_map.clear()
        self.scene_map.territory_items.clear()
        self.scene_map._draw_ocean()
        self.scene_map._draw_grid()
        self.scene_map._draw_connections()
        self.scene_map._draw_territories()
        self.scene_map._draw_continent_labels()
        self.scene_map._draw_tokens()

# ─────────────────────────────────────────────────────
#  PLAYER HUD BAR
# ─────────────────────────────────────────────────────

import os

PLAYER_ACCENT = [
    {"base": "rgba(160,30,20,0.30)",  "border": QColor(220,70,55),  "glow": QColor(240,200,64)},
    {"base": "rgba(25,60,160,0.30)",  "border": QColor(70,130,230), "glow": QColor(240,200,64)},
]

class PortraitLabel(QLabel):
    """Square portrait with rounded border; falls back to initials."""
    def __init__(self, image_path: str, initials: str, accent: dict, size=54):
        super().__init__()
        self.setFixedSize(size, size)
        loaded = False
        if image_path and os.path.exists(image_path):
            px = QPixmap(image_path)
            if not px.isNull():
                px = px.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
                # centre-crop
                x = (px.width()  - size) // 2
                y = (px.height() - size) // 2
                px = px.copy(x, y, size, size)
                self.setPixmap(px)
                self.setScaledContents(False)
                loaded = True
        if not loaded:
            self.setText(initials)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont("Georgia", 20, QFont.Weight.Bold)
            self.setFont(font)
            self.setStyleSheet(f"""
                color: {accent["glow"]};
                background-color: {accent["base"]};
                border: 2px solid {accent["border"]};
                border-radius: 6px;
            """)
        else:
            self.setStyleSheet(f"""
                border: 2px solid {accent["border"]};
                border-radius: 6px;
            """)

class PlayerCard(QFrame):
    def __init__(self, idx, name, image_path, turn_label_right=False):
        super().__init__()
        self.idx = idx
        self.accent = PLAYER_ACCENT[idx]
        self._is_active = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        if turn_label_right:
            layout.setDirection(QHBoxLayout.Direction.RightToLeft)

        # portrait
        initials = name[0].upper() if name else "?"
        self.portrait = PortraitLabel(image_path, initials, self.accent)

        # text block
        text_block = QWidget()
        text_block.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(text_block)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(3)
        if turn_label_right:
            tl.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_lbl = QLabel(name.upper())
        self.name_lbl.setStyleSheet(
            "color: #e8dfc8; font-family: Georgia; font-size: 13px;"
            "font-weight: bold; letter-spacing: 2px; background: transparent;")

        self.status_lbl = QLabel("◇ bekliyor")
        self.status_lbl.setStyleSheet(
            "color: rgba(180,180,180,100); font-family: Andale Mono;"
            "font-size: 9px; letter-spacing: 2px; background: transparent;")

        # stats row
        stats_row = QWidget()
        stats_row.setStyleSheet("background: transparent;")
        sl = QHBoxLayout(stats_row)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(10)
        if turn_label_right:
            sl.setDirection(QHBoxLayout.Direction.RightToLeft)

        self.territory_lbl = self._stat("0", "BÖLGE", self.accent["glow"])
        self.army_lbl      = self._stat("0", "ORDU",  "#888888")
        sl.addWidget(self.territory_lbl)
        sl.addWidget(self.army_lbl)
        sl.addStretch()

        tl.addWidget(self.name_lbl)
        tl.addWidget(self.status_lbl)
        tl.addWidget(stats_row)

        layout.addWidget(self.portrait)
        layout.addWidget(text_block, stretch=1)

        self._set_inactive()

    def _stat(self, val, label, color):
        w = QLabel(f'<span style="color:{color};font-size:12px;font-weight:bold;">{val}</span>'
                   f'<span style="color:rgba(150,140,120,130);font-size:8px;letter-spacing:1px;"> {label}</span>')
        w.setStyleSheet("background: transparent;")
        w.setTextFormat(Qt.TextFormat.RichText)
        return w

    def _set_active(self):
        self.setStyleSheet(f"""
            background-color: {self.accent["base"]};
            border: 1px solid {self.accent["border"]};
            border-radius: 8px;
        """)
        self.status_lbl.setText("◆ SIRA SENDE")
        self.status_lbl.setStyleSheet(
            "color: #f0c840; font-family: Andale Mono;"
            "font-size: 9px; letter-spacing: 2px; background: transparent;")
        self.portrait.setStyleSheet(
            f"border: 2px solid #c8a840; border-radius: 6px;")

    def _set_inactive(self):
        self.setStyleSheet("""
            background-color: rgba(255,255,255,6);
            border: 1px solid rgba(255,255,255,15);
            border-radius: 8px;
        """)
        self.status_lbl.setText("◇ bekliyor")
        self.status_lbl.setStyleSheet(
            "color: rgba(180,180,180,100); font-family: Andale Mono;"
            "font-size: 9px; letter-spacing: 2px; background: transparent;")
        self.portrait.setStyleSheet(
            f"border: 2px solid {self.accent['border']}; border-radius: 6px;")

    def set_active(self, active: bool):
        self._is_active = active
        self._set_active() if active else self._set_inactive()

    def update_stats(self, territories: int, armies: int):
        c = self.accent["glow"]
        self.territory_lbl.setText(
            f'<span style="color:{c};font-size:12px;font-weight:bold;">{territories}</span>'
            f'<span style="color:rgba(150,140,120,130);font-size:8px;letter-spacing:1px;"> BÖLGE</span>')
        self.army_lbl.setText(
            f'<span style="color:#888;font-size:12px;font-weight:bold;">{armies}</span>'
            f'<span style="color:rgba(150,140,120,130);font-size:8px;letter-spacing:1px;"> ORDU</span>')

class PlayerHUD(QWidget):
    PHASES = ["TAKVİYE", "SALDIRI", "HAREKET"]

    def __init__(self, player_names=("Oyuncu 1", "Oyuncu 2"),
                 image_paths=("", ""), current_turn=0):
        super().__init__()
        self.player_names  = list(player_names)
        self.image_paths   = list(image_paths)
        self.current_turn  = current_turn
        self.turn_number   = 1
        self.current_phase = 0
        self.setFixedHeight(80)
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── top strip ──
        top = QWidget()
        top.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 rgba(30,50,90,180), stop:1 rgba(5,12,35,230));"
            "border-bottom: 1px solid rgba(180,140,50,60);")
        top.setFixedHeight(62)
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(12, 6, 12, 6)
        top_l.setSpacing(0)

        self.card0 = PlayerCard(0, player_names[0], image_paths[0], turn_label_right=False)
        self.card1 = PlayerCard(1, player_names[1], image_paths[1], turn_label_right=True)

        # centre: turn badge
        centre = QWidget()
        centre.setFixedWidth(70)
        centre.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(centre)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(2)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.turn_lbl = QLabel("1")
        self.turn_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_lbl.setFixedSize(34, 34)
        self.turn_lbl.setStyleSheet(
            "color: #c8a840; font-family: Georgia; font-size: 14px; font-weight: bold;"
            "background: rgba(5,12,35,200); border: 1px solid rgba(180,140,50,120);"
            "border-radius: 17px;")

        tur_label = QLabel("TUR")
        tur_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tur_label.setStyleSheet(
            "color: rgba(180,140,50,100); font-family: Andale Mono;"
            "font-size: 7px; letter-spacing: 2px; background: transparent;")

        cl.addWidget(self.turn_lbl, 0, Qt.AlignmentFlag.AlignHCenter)
        cl.addWidget(tur_label,     0, Qt.AlignmentFlag.AlignHCenter)

        top_l.addWidget(self.card0, stretch=1)
        top_l.addWidget(centre)
        top_l.addWidget(self.card1, stretch=1)

        # ── phase bar ──
        phase_bar = QWidget()
        phase_bar.setFixedHeight(18)
        phase_bar.setStyleSheet("background: rgba(5,12,35,210);")
        pb_l = QHBoxLayout(phase_bar)
        pb_l.setContentsMargins(0, 0, 0, 0)
        pb_l.setSpacing(0)
        pb_l.addStretch()

        self._phase_labels = []
        for i, ph in enumerate(self.PHASES):
            lbl = QLabel(ph)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._phase_labels.append(lbl)
            pb_l.addWidget(lbl)
            if i < len(self.PHASES) - 1:
                sep = QLabel("  ›  ")
                sep.setStyleSheet(
                    "color: rgba(180,160,120,60); font-size: 9px; background: transparent;")
                pb_l.addWidget(sep)

        pb_l.addStretch()

        root.addWidget(top)
        root.addWidget(phase_bar)

        self._refresh()

    def _refresh(self):
        self.card0.set_active(self.current_turn == 0)
        self.card1.set_active(self.current_turn == 1)
        self.turn_lbl.setText(str(self.turn_number))

        for i, lbl in enumerate(self._phase_labels):
            if i == self.current_phase:
                lbl.setStyleSheet(
                    "color: #c8a840; font-family: Andale Mono; font-size: 9px;"
                    "letter-spacing: 2px; background: transparent; padding: 0 8px;")
            else:
                lbl.setStyleSheet(
                    "color: rgba(180,160,120,80); font-family: Andale Mono; font-size: 9px;"
                    "letter-spacing: 2px; background: transparent; padding: 0 8px;")

    def set_turn(self, player_idx: int):
        self.current_turn = player_idx
        self._refresh()

    def next_turn(self):
        next_p = (self.current_turn + 1) % 2
        if next_p == 0:
            self.turn_number += 1
        self.current_turn = next_p
        self.current_phase = 0
        self._refresh()

    def next_phase(self):
        if self.current_phase < len(self.PHASES) - 1:
            self.current_phase += 1
        else:
            self.next_turn()
        self._refresh()

    def set_player_icon(self, player_idx: int, image_path: str):
        card = self.card0 if player_idx == 0 else self.card1
        initials = self.player_names[player_idx][0].upper()
        accent = PLAYER_ACCENT[player_idx]
        new_portrait = PortraitLabel(image_path, initials, accent)
        old = card.portrait
        card.layout().replaceWidget(old, new_portrait)
        old.deleteLater()
        card.portrait = new_portrait

    def update_stats(self, player_idx: int, territories: int, armies: int):
        card = self.card0 if player_idx == 0 else self.card1
        card.update_stats(territories, armies)

class GameWindow(QMainWindow):
    def __init__(self, player_names=("Oyuncu 1", "Oyuncu 2"), image_paths=("", "")):
        super().__init__()

        # 1. Hande'nin Qt Designer iskeletini kuruyoruz
        self.ui = Ui_GameWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Risk — Dünya Haritası")
        self.setStyleSheet("background-color: #0a1e46;")

        # 2. Özel bileşenlerimizi (HUD ve Harita) yaratıyoruz
        self.hud = PlayerHUD(player_names=player_names, image_paths=image_paths, current_turn=0)
        self.map_view = GameMapView()

        # Araya ince şık bir çizgi (Divider)
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(200, 160, 50, 80);")

        # 3. Bileşenleri Hande'nin tasarımına yerleştiriyoruz
        # NOT: Eğer Hande Qt Designer'da bir Layout (örneğin verticalLayout) açtıysa:
        # self.ui.verticalLayout.addWidget(self.hud) gibi eklemelisin.
        # Eğer özel bir layout yoksa, centralWidget üzerine biz kurarız:

        layout = QVBoxLayout(self.ui.centralwidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.hud)
        layout.addWidget(div)
        layout.addWidget(self.map_view, stretch=1)

        # Haritayı ekrana tam oturtma ayarı
        self.map_view.fitInView(
            self.map_view.scene_map.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio
        )