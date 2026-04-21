import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsLineItem, QGraphicsPathItem, QGraphicsRectItem,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import (
    QPolygonF, QColor, QPen, QBrush, QFont, QPainter,
    QRadialGradient, QLinearGradient, QPainterPath, QFontMetrics, QPixmap
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF

# ─────────────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────────────
PALETTE = {
    "north_america": {"base": QColor(52, 120, 180),  "light": QColor(90, 160, 220),  "dark": QColor(25, 75, 130)},
    "south_america": {"base": QColor(195, 100, 30),  "light": QColor(235, 140, 60),  "dark": QColor(140, 65, 10)},
    "europe":        {"base": QColor(140, 100, 210), "light": QColor(175, 140, 245), "dark": QColor(90, 55, 155)},
    "africa":        {"base": QColor(155, 120, 65),  "light": QColor(195, 160, 100), "dark": QColor(105, 75, 30)},
    "asia":          {"base": QColor(55, 145, 65),   "light": QColor(90, 185, 100),  "dark": QColor(25, 95, 35)},
    "australia":     {"base": QColor(205, 155, 40),  "light": QColor(245, 195, 75),  "dark": QColor(155, 110, 10)},
}

OCEAN_DEEP   = QColor(15,  45,  90)
OCEAN_MID    = QColor(25,  70,  135)
BORDER_DARK  = QColor(10,  10,  10)
BORDER_SEL   = QColor(255, 230, 0)
CONN_COLOR   = QColor(180, 220, 255, 60)

# ─────────────────────────────────────────────────────
#  TERRITORY DATA  (refined polygons — more points)
# ─────────────────────────────────────────────────────
TERRITORIES = [
    # ══ NORTH AMERICA ══
    {"id":"alaska",            "label":"Alaska",         "continent":"north_america",
     "poly":[(58,78),(80,65),(108,58),(138,68),(148,82),(145,108),(118,125),(90,128),(65,112)],
     "tp":(105,92),"troops":1},

    {"id":"northwest_territory","label":"NW Territory",  "continent":"north_america",
     "poly":[(108,58),(148,48),(200,42),(225,52),(235,78),(225,98),(200,115),(165,120),(145,108),(138,68)],
     "tp":(180,78),"troops":3},

    {"id":"greenland",         "label":"Greenland",      "continent":"north_america",
     "poly":[(258,15),(305,8),(355,8),(378,22),(382,52),(370,78),(335,95),(295,98),(262,80),(245,52)],
     "tp":(318,50),"troops":2},

    {"id":"alberta",           "label":"Alberta",        "continent":"north_america",
     "poly":[(125,128),(165,120),(200,115),(222,132),(225,158),(210,188),(185,198),(158,195),(135,178),(122,155)],
     "tp":(172,158),"troops":1},

    {"id":"ontario",           "label":"Ontario",        "continent":"north_america",
     "poly":[(200,115),(235,108),(268,108),(295,118),(308,142),(298,168),(275,188),(245,195),(210,188),(225,158),(222,132)],
     "tp":(255,148),"troops":4},

    {"id":"quebec",            "label":"Quebec",         "continent":"north_america",
     "poly":[(268,108),(295,98),(335,95),(352,108),(358,135),(348,162),(322,172),(295,168),(308,142),(295,118)],
     "tp":(318,135),"troops":2},

    {"id":"western_us",        "label":"Western US",     "continent":"north_america",
     "poly":[(122,198),(158,195),(185,198),(210,188),(215,215),(212,248),(200,278),(175,292),(148,288),(128,265),(118,232)],
     "tp":(168,242),"troops":5},

    {"id":"eastern_us",        "label":"Eastern US",     "continent":"north_america",
     "poly":[(210,188),(245,195),(275,188),(298,168),(312,188),(318,218),(308,255),(285,282),(255,288),(225,280),(200,258),(212,225),(215,215)],
     "tp":(262,232),"troops":3},

    {"id":"central_america",   "label":"C. America",     "continent":"north_america",
     "poly":[(148,288),(175,292),(200,285),(218,298),(225,322),(215,345),(195,358),(172,352),(155,332),(142,308)],
     "tp":(185,318),"troops":1},

    # ══ SOUTH AMERICA ══
    {"id":"venezuela",         "label":"Venezuela",      "continent":"south_america",
     "poly":[(165,358),(195,352),(228,355),(242,375),(238,398),(218,412),(195,415),(172,402),(162,382)],
     "tp":(200,382),"troops":2},

    {"id":"peru",              "label":"Peru",           "continent":"south_america",
     "poly":[(155,415),(195,415),(218,412),(228,432),(222,462),(205,478),(182,482),(162,465),(148,440)],
     "tp":(185,445),"troops":1},

    {"id":"brazil",            "label":"Brazil",         "continent":"south_america",
     "poly":[(218,412),(242,398),(268,382),(298,372),(318,385),(325,412),(315,445),(295,468),(268,478),(242,475),(222,462),(228,432)],
     "tp":(272,422),"troops":3},

    {"id":"argentina",         "label":"Argentina",      "continent":"south_america",
     "poly":[(162,482),(205,478),(242,475),(258,498),(255,528),(242,555),(222,572),(198,568),(175,548),(162,518)],
     "tp":(208,522),"troops":1},

    # ══ EUROPE ══
    {"id":"iceland",           "label":"Iceland",        "continent":"europe",
     "poly":[(392,58),(418,48),(448,52),(458,72),(448,95),(422,102),(398,90)],
     "tp":(425,72),"troops":1},

    {"id":"great_britain",     "label":"Gt. Britain",    "continent":"europe",
     "poly":[(405,108),(428,98),(452,102),(462,122),(458,148),(442,162),(418,165),(405,148),(398,125)],
     "tp":(430,132),"troops":2},

    {"id":"northern_europe",   "label":"N. Europe",      "continent":"europe",
     "poly":[(448,118),(478,108),(508,112),(518,135),(512,158),(492,172),(465,172),(448,155)],
     "tp":(482,140),"troops":1},

    {"id":"scandinavia",       "label":"Scandinavia",    "continent":"europe",
     "poly":[(455,48),(492,38),(528,38),(542,58),(545,85),(528,105),(505,108),(478,108),(455,92)],
     "tp":(498,70),"troops":3},

    {"id":"ukraine",           "label":"Ukraine",        "continent":"europe",
     "poly":[(518,78),(558,68),(598,65),(628,72),(635,98),(625,128),(608,148),(578,155),(548,148),(518,135),(508,112)],
     "tp":(572,108),"troops":1},

    {"id":"western_europe",    "label":"W. Europe",      "continent":"europe",
     "poly":[(405,165),(442,162),(462,165),(478,185),(472,215),(452,228),(428,228),(408,215),(398,192)],
     "tp":(438,195),"troops":2},

    {"id":"southern_europe",   "label":"S. Europe",      "continent":"europe",
     "poly":[(462,165),(492,172),(518,165),(535,182),(538,205),(522,222),(498,228),(472,225),(458,208),(462,185)],
     "tp":(498,195),"troops":1},

    # ══ AFRICA ══
    {"id":"north_africa",      "label":"N. Africa",      "continent":"africa",
     "poly":[(408,232),(452,228),(498,228),(535,222),(558,228),(568,255),(555,295),(535,322),(508,332),(475,328),(445,312),(422,288),(408,262)],
     "tp":(482,275),"troops":3},

    {"id":"egypt",             "label":"Egypt",          "continent":"africa",
     "poly":[(535,222),(565,218),(592,222),(602,248),(592,272),(568,278),(548,268),(538,248)],
     "tp":(565,248),"troops":2},

    {"id":"east_africa",       "label":"E. Africa",      "continent":"africa",
     "poly":[(555,295),(585,278),(608,275),(618,298),(622,328),(608,358),(585,372),(562,362),(542,338),(535,312)],
     "tp":(578,322),"troops":1},

    {"id":"congo",             "label":"Congo",          "continent":"africa",
     "poly":[(475,328),(508,332),(535,322),(548,338),(548,368),(535,382),(508,385),(482,378),(465,358),(465,342)],
     "tp":(508,355),"troops":3},

    {"id":"south_africa",      "label":"S. Africa",      "continent":"africa",
     "poly":[(465,378),(508,378),(535,382),(552,398),(555,428),(542,455),(518,465),(492,462),(472,445),(458,415),(458,392)],
     "tp":(508,422),"troops":1},

    {"id":"madagascar",        "label":"Madagascar",     "continent":"africa",
     "poly":[(588,368),(612,362),(625,382),(622,412),(608,425),(590,418),(578,398)],
     "tp":(601,392),"troops":1},

    # ══ ASIA ══
    {"id":"middle_east",       "label":"Middle East",    "continent":"asia",
     "poly":[(575,215),(608,208),(638,202),(655,218),(658,248),(645,272),(618,282),(592,278),(572,258),(568,232)],
     "tp":(612,242),"troops":2},

    {"id":"afghanistan",       "label":"Afghanistan",    "continent":"asia",
     "poly":[(632,138),(665,128),(702,128),(718,148),(722,172),(708,192),(682,202),(655,195),(638,172),(628,152)],
     "tp":(675,162),"troops":1},

    {"id":"ural",              "label":"Ural",           "continent":"asia",
     "poly":[(635,68),(672,58),(712,55),(728,72),(732,105),(718,128),(695,138),(665,132),(642,115),(632,92)],
     "tp":(682,95),"troops":3},

    {"id":"siberia",           "label":"Siberia",        "continent":"asia",
     "poly":[(712,48),(758,38),(802,35),(825,48),(828,78),(818,108),(798,125),(765,128),(732,118),(718,95),(728,72)],
     "tp":(768,78),"troops":2},

    {"id":"yakutsk",           "label":"Yakutsk",        "continent":"asia",
     "poly":[(798,35),(842,28),(878,28),(892,48),(888,78),(872,102),(848,108),(818,102),(800,80),(802,58)],
     "tp":(842,65),"troops":1},

    {"id":"kamchatka",         "label":"Kamchatka",      "continent":"asia",
     "poly":[(878,32),(918,25),(948,32),(962,55),(958,85),(942,112),(918,122),(892,112),(875,88),(875,55)],
     "tp":(912,72),"troops":4},

    {"id":"irkutsk",           "label":"Irkutsk",        "continent":"asia",
     "poly":[(798,125),(828,112),(862,108),(878,125),(878,152),(862,172),(835,178),(808,172),(792,152)],
     "tp":(835,148),"troops":1},

    {"id":"mongolia",          "label":"Mongolia",       "continent":"asia",
     "poly":[(765,128),(798,118),(828,118),(858,128),(862,152),(848,178),(822,195),(795,202),(768,195),(752,172),(755,148)],
     "tp":(805,162),"troops":2},

    {"id":"japan",             "label":"Japan",          "continent":"asia",
     "poly":[(905,135),(932,128),(948,142),(952,168),(938,185),(915,188),(898,172),(895,152)],
     "tp":(922,158),"troops":1},

    {"id":"china",             "label":"China",          "continent":"asia",
     "poly":[(718,155),(752,145),(795,145),(822,158),(835,182),(822,208),(808,228),(785,245),(755,255),(728,248),(708,228),(698,205),(708,178)],
     "tp":(762,198),"troops":5},

    {"id":"india",             "label":"India",          "continent":"asia",
     "poly":[(655,218),(692,208),(718,212),(732,232),(732,262),(718,295),(702,312),(678,318),(658,302),(645,272),(645,242)],
     "tp":(688,262),"troops":2},

    {"id":"siam",              "label":"Siam",           "continent":"asia",
     "poly":[(755,248),(790,238),(818,238),(828,258),(825,288),(808,312),(785,322),(762,315),(748,292),(748,268)],
     "tp":(785,278),"troops":1},

    # ══ AUSTRALIA ══
    {"id":"indonesia",         "label":"Indonesia",      "continent":"australia",
     "poly":[(795,325),(838,315),(868,318),(878,342),(872,368),(848,378),(818,375),(795,355),(782,338)],
     "tp":(828,348),"troops":3},

    {"id":"new_guinea",        "label":"New Guinea",     "continent":"australia",
     "poly":[(872,298),(912,292),(938,295),(948,315),(945,338),(922,352),(895,355),(868,342),(862,318)],
     "tp":(905,322),"troops":1},

    {"id":"western_australia", "label":"W. Australia",   "continent":"australia",
     "poly":[(795,385),(842,375),(875,378),(885,405),(882,438),(865,462),(838,472),(808,465),(788,442),(782,412)],
     "tp":(832,425),"troops":2},

    {"id":"eastern_australia", "label":"E. Australia",   "continent":"australia",
     "poly":[(882,375),(922,365),(952,368),(965,395),(962,428),(945,458),(918,472),(888,468),(872,442),(875,408)],
     "tp":(918,418),"troops":4},
]

CONNECTIONS = [
    ("alaska","northwest_territory"),("alaska","alberta"),("alaska","kamchatka"),
    ("northwest_territory","greenland"),("northwest_territory","alberta"),("northwest_territory","ontario"),
    ("greenland","ontario"),("greenland","quebec"),("greenland","iceland"),
    ("alberta","ontario"),("alberta","western_us"),
    ("ontario","quebec"),("ontario","eastern_us"),("ontario","western_us"),
    ("quebec","eastern_us"),
    ("western_us","eastern_us"),("western_us","central_america"),
    ("eastern_us","central_america"),
    ("central_america","venezuela"),
    ("venezuela","peru"),("venezuela","brazil"),
    ("peru","brazil"),("peru","argentina"),
    ("brazil","argentina"),("brazil","north_africa"),
    ("iceland","great_britain"),("iceland","scandinavia"),
    ("great_britain","northern_europe"),("great_britain","western_europe"),
    ("scandinavia","northern_europe"),("scandinavia","ukraine"),
    ("northern_europe","ukraine"),("northern_europe","western_europe"),("northern_europe","southern_europe"),
    ("western_europe","southern_europe"),("western_europe","north_africa"),
    ("southern_europe","ukraine"),("southern_europe","north_africa"),("southern_europe","egypt"),
    ("ukraine","ural"),("ukraine","afghanistan"),("ukraine","middle_east"),
    ("north_africa","egypt"),("north_africa","east_africa"),("north_africa","congo"),
    ("egypt","east_africa"),("egypt","middle_east"),
    ("east_africa","congo"),("east_africa","south_africa"),("east_africa","madagascar"),("east_africa","middle_east"),
    ("congo","south_africa"),
    ("south_africa","madagascar"),
    ("middle_east","afghanistan"),("middle_east","india"),
    ("afghanistan","ural"),("afghanistan","china"),("afghanistan","india"),
    ("ural","siberia"),("ural","china"),
    ("siberia","yakutsk"),("siberia","irkutsk"),("siberia","mongolia"),("siberia","china"),
    ("yakutsk","kamchatka"),("yakutsk","irkutsk"),
    ("kamchatka","irkutsk"),("kamchatka","mongolia"),("kamchatka","japan"),
    ("irkutsk","mongolia"),
    ("mongolia","china"),("mongolia","japan"),
    ("china","india"),("china","siam"),
    ("india","siam"),
    ("siam","indonesia"),
    ("indonesia","new_guinea"),("indonesia","western_australia"),
    ("new_guinea","eastern_australia"),("new_guinea","western_australia"),
    ("western_australia","eastern_australia"),
]

CONTINENT_LABELS = [
    {"text": "NORTH\nAMERICA", "x": 185, "y": 155, "continent": "north_america"},
    {"text": "SOUTH\nAMERICA", "x": 220, "y": 415, "continent": "south_america"},
    {"text": "EUROPE",         "x": 468, "y": 120, "continent": "europe"},
    {"text": "AFRICA",         "x": 488, "y": 360, "continent": "africa"},
    {"text": "ASIA",           "x": 765, "y": 105, "continent": "asia"},
    {"text": "AUSTRALIA",      "x": 858, "y": 398, "continent": "australia"},
]


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
        self.base_color  = pal["base"]
        self.light_color = pal["light"]
        self.dark_color  = pal["dark"]
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
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
import os

PLAYER_ACCENT = [
    {"base": "rgba(160,30,20,0.30)",  "border": QColor(220,70,55),  "glow": QColor(240,200,64)},
    {"base": "rgba(25,60,160,0.30)",  "border": QColor(70,130,230), "glow": QColor(240,200,64)},
]


class CirclePortrait(QLabel):
    """Circular portrait: clips image into a circle via paintEvent."""
    def __init__(self, image_path, initials, accent, size=68):
        super().__init__()
        self.setFixedSize(size, size)
        self._size   = size
        self._accent = accent
        self._active = False
        self._initials = initials
        self._pixmap = None

        if image_path and os.path.exists(image_path):
            px = QPixmap(image_path)
            if not px.isNull():
                px = px.scaled(size, size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation)
                ox = (px.width()  - size) // 2
                oy = (px.height() - size) // 2
                self._pixmap = px.copy(ox, oy, size, size)

    def set_active(self, active):
        self._active = active
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainterPath
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = self._size
        r = s // 2

        # clip circle
        path = QPainterPath()
        path.addEllipse(QPointF(r, r), r - 2, r - 2)
        p.setClipPath(path)

        if self._pixmap:
            p.drawPixmap(0, 0, self._pixmap)
        else:
            # fallback: filled circle with initial
            bc = self._accent["border"]
            p.fillRect(0, 0, s, s, QColor(bc.red(), bc.green(), bc.blue(), 60))
            p.setFont(QFont("Georgia", s // 3, QFont.Weight.Bold))
            p.setPen(QPen(self._accent["border"]))
            p.drawText(0, 0, s, s, Qt.AlignmentFlag.AlignCenter, self._initials)

        p.setClipping(False)

        # border ring
        border_color = self._accent["glow"] if self._active else self._accent["border"]
        pen = QPen(border_color, 3 if self._active else 2)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(2, 2, s - 4, s - 4)

        # outer glow ring when active
        if self._active:
            glow_pen = QPen(QColor(212, 160, 48, 60), 6)
            p.setPen(glow_pen)
            p.drawEllipse(1, 1, s - 2, s - 2)
        p.end()


class PlayerCard(QFrame):
    def __init__(self, idx, name, image_path, mirror=False):
        super().__init__()
        self.idx     = idx
        self.mirror  = mirror
        self._accent = PLAYER_ACCENT[idx]
        self.setFixedHeight(82)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 8, 14, 8)
        row.setSpacing(14)
        if mirror:
            row.setDirection(QHBoxLayout.Direction.RightToLeft)

        # portrait
        initials = (name[0].upper() if name else "?")
        self.portrait = CirclePortrait(image_path, initials, self._accent)

        # text column
        col = QWidget()
        col.setStyleSheet("background:transparent;")
        col.setSizePolicy(col.sizePolicy().horizontalPolicy(),
                          col.sizePolicy().verticalPolicy())
        cl = QVBoxLayout(col)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(4)
        if mirror:
            cl.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_lbl = QLabel(name.upper())
        self.name_lbl.setStyleSheet(
            "color:#ede0c4;font-family:Georgia;font-size:14px;"
            "font-weight:bold;letter-spacing:2px;background:transparent;")

        self.status_lbl = QLabel("◇ bekliyor")
        self.status_lbl.setStyleSheet(
            "color:rgba(180,180,180,80);font-family:'Andale Mono';"
            "font-size:9px;letter-spacing:2px;background:transparent;")

        # stats
        stats_w = QWidget()
        stats_w.setStyleSheet("background:transparent;")
        stl = QHBoxLayout(stats_w)
        stl.setContentsMargins(0, 0, 0, 0)
        stl.setSpacing(12)
        if mirror:
            stl.setDirection(QHBoxLayout.Direction.RightToLeft)

        self.terr_lbl = self._stat_pair("0", "BÖLGE")
        self.army_lbl = self._stat_pair("0", "ORDU")
        dot = QLabel("·")
        dot.setStyleSheet("color:rgba(180,150,60,100);font-size:14px;background:transparent;")

        stl.addWidget(self.terr_lbl)
        stl.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
        stl.addWidget(self.army_lbl)
        stl.addStretch()

        cl.addWidget(self.name_lbl)
        cl.addWidget(self.status_lbl)
        cl.addWidget(stats_w)

        row.addWidget(self.portrait, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(col, 1)

        self._set_inactive()

    def _stat_pair(self, val, label):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(1)
        v = QLabel(val)
        v.setStyleSheet(
            "color:#e8d8b0;font-family:Georgia;font-size:17px;"
            "font-weight:bold;background:transparent;")
        l = QLabel(label)
        l.setStyleSheet(
            "color:rgba(180,165,130,100);font-family:'Andale Mono';"
            "font-size:7px;letter-spacing:2px;background:transparent;")
        vl.addWidget(v)
        vl.addWidget(l)
        setattr(w, '_val_lbl', v)
        return w

    def _set_active(self):
        a = self._accent
        self.setStyleSheet(
            f"background-color:{a['base']};"
            f"border:1px solid rgba({a['border'].red()},{a['border'].green()},{a['border'].blue()},120);"
            "border-radius:8px;")
        self.status_lbl.setText("◆ SIRA SENDE")
        self.status_lbl.setStyleSheet(
            "color:#f0c840;font-family:'Andale Mono';"
            "font-size:9px;letter-spacing:2px;background:transparent;")
        self.portrait.set_active(True)

    def _set_inactive(self):
        self.setStyleSheet(
            "background-color:rgba(255,255,255,5);"
            "border:1px solid rgba(255,255,255,15);"
            "border-radius:8px;")
        self.status_lbl.setText("◇ bekliyor")
        self.status_lbl.setStyleSheet(
            "color:rgba(180,180,180,80);font-family:'Andale Mono';"
            "font-size:9px;letter-spacing:2px;background:transparent;")
        self.portrait.set_active(False)

    def set_active(self, active):
        self._set_active() if active else self._set_inactive()

    def update_stats(self, territories, armies):
        self.terr_lbl._val_lbl.setText(str(territories))
        self.army_lbl._val_lbl.setText(str(armies))


class PlayerHUD(QWidget):
    PHASES = ["TAKVİYE", "SALDIRI", "HAREKET"]

    def __init__(self, player_names=("Oyuncu 1", "Oyuncu 2"),
                 image_paths=("", ""), current_turn=0):
        super().__init__()
        self.player_names  = list(player_names)
        self.current_turn  = current_turn
        self.turn_number   = 1
        self.current_phase = 0
        self.setFixedHeight(110)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── main strip ──
        self.strip = QFrame()
        self.strip.setFixedHeight(84)
        sl = QHBoxLayout(self.strip)
        sl.setContentsMargins(10, 0, 10, 0)
        sl.setSpacing(8)

        self.card0 = PlayerCard(0, player_names[0], image_paths[0], mirror=False)
        self.card1 = PlayerCard(1, player_names[1], image_paths[1], mirror=True)

        # centre badge
        centre = QWidget()
        centre.setFixedWidth(78)
        centre.setStyleSheet("background:transparent;")
        cl2 = QVBoxLayout(centre)
        cl2.setContentsMargins(0, 0, 0, 0)
        cl2.setSpacing(4)
        cl2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vs = QLabel("VS")
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setStyleSheet(
            "color:rgba(180,140,50,120);font-family:Georgia;"
            "font-size:20px;font-weight:bold;letter-spacing:3px;background:transparent;")

        self.turn_badge = QLabel("TUR 1")
        self.turn_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_badge.setFixedHeight(20)
        self.turn_badge.setStyleSheet(
            "color:#c8a840;font-family:'Andale Mono';font-size:8px;"
            "letter-spacing:2px;background:rgba(5,12,35,180);"
            "border:1px solid rgba(180,140,50,80);border-radius:10px;padding:0 8px;")

        cl2.addWidget(vs)
        cl2.addWidget(self.turn_badge, 0, Qt.AlignmentFlag.AlignHCenter)

        sl.addWidget(self.card0, stretch=1)
        sl.addWidget(centre,    stretch=0)
        sl.addWidget(self.card1, stretch=1)

        # ── phase bar ──
        phase_w = QFrame()
        phase_w.setFixedHeight(26)
        phase_w.setStyleSheet(
            "background:rgba(5,10,30,250);"
            "border-top:1px solid rgba(180,140,50,40);")
        pl = QHBoxLayout(phase_w)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(0)
        pl.addStretch()
        self._phase_lbls = []
        for i, ph in enumerate(self.PHASES):
            lbl = QLabel(ph)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._phase_lbls.append(lbl)
            pl.addWidget(lbl)
            if i < len(self.PHASES) - 1:
                sep = QLabel("  ›  ")
                sep.setStyleSheet(
                    "color:rgba(180,160,120,50);font-size:9px;background:transparent;")
                pl.addWidget(sep)
        pl.addStretch()

        root.addWidget(self.strip)
        root.addWidget(phase_w)
        self._refresh()

    def _refresh(self):
        colors = [
            ("rgba(160,30,20,0.28)", "rgba(8,18,50,0.98)"),
            ("rgba(8,18,50,0.98)",   "rgba(25,60,165,0.28)"),
        ]
        l, r = colors[self.current_turn]
        self.strip.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {l},stop:0.42 rgba(8,18,50,0.98),"
            f"stop:0.58 rgba(8,18,50,0.98),stop:1 {r});"
            "border-bottom:1px solid rgba(180,140,50,40);")
        self.card0.set_active(self.current_turn == 0)
        self.card1.set_active(self.current_turn == 1)
        self.turn_badge.setText(f"TUR {self.turn_number}")
        for i, lbl in enumerate(self._phase_lbls):
            if i == self.current_phase:
                lbl.setStyleSheet(
                    "color:#c8a840;font-family:'Andale Mono';font-size:9px;"
                    "letter-spacing:2px;background:transparent;padding:0 10px;font-weight:bold;")
            else:
                lbl.setStyleSheet(
                    "color:rgba(180,160,120,60);font-family:'Andale Mono';font-size:9px;"
                    "letter-spacing:2px;background:transparent;padding:0 10px;")

    def set_turn(self, player_idx):
        self.current_turn = player_idx
        self._refresh()

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % 2
        if self.current_turn == 0:
            self.turn_number += 1
        self.current_phase = 0
        self._refresh()

    def next_phase(self):
        if self.current_phase < len(self.PHASES) - 1:
            self.current_phase += 1
        else:
            self.next_turn()
        self._refresh()

    def set_player_icon(self, player_idx, image_path):
        card = self.card0 if player_idx == 0 else self.card1
        accent   = PLAYER_ACCENT[player_idx]
        initials = self.player_names[player_idx][0].upper()
        new_p    = CirclePortrait(image_path, initials, accent)
        card.layout().replaceWidget(card.portrait, new_p)
        card.portrait.deleteLater()
        card.portrait = new_p

    def update_stats(self, player_idx, territories, armies):
        card = self.card0 if player_idx == 0 else self.card1
        card.update_stats(territories, armies)



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
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
import os

PLAYER_ACCENT = [
    {"base": "rgba(160,30,20,0.35)",  "border": "rgba(220,70,55,0.45)",  "glow": "#dc3c37"},
    {"base": "rgba(25,60,160,0.35)",  "border": "rgba(70,130,230,0.45)", "glow": "#4682dc"},
]


class PortraitLabel(QLabel):
    def __init__(self, image_path, initials, accent, size=72):
        super().__init__()
        self.setFixedSize(size, size)
        self._size = size
        self._accent = accent
        loaded = False
        if image_path and os.path.exists(image_path):
            px = QPixmap(image_path)
            if not px.isNull():
                px = px.scaled(size, size,
                               Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
                x = (px.width()  - size) // 2
                y = (px.height() - size) // 2
                px = px.copy(x, y, size, size)
                self.setPixmap(px)
                self.setScaledContents(False)
                loaded = True
        if not loaded:
            self.setText(initials)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setFont(QFont("Georgia", 26, QFont.Weight.Bold))
        self._set_inactive()

    def _border_style(self, active):
        if active:
            return (f"border: 3px solid #d4a030;"
                    f"border-radius: {self._size//2}px;"
                    f"background-color: {self._accent['base']};"
                    f"color: {self._accent['glow']};")
        return (f"border: 3px solid {self._accent['border']};"
                f"border-radius: {self._size//2}px;"
                f"background-color: {self._accent['base']};"
                f"color: {self._accent['glow']};")

    def _set_active(self):   self.setStyleSheet(self._border_style(True))
    def _set_inactive(self): self.setStyleSheet(self._border_style(False))


class PlayerCard(QFrame):
    SCALE_BIG  = 1.15
    SCALE_NORM = 1.0

    def __init__(self, idx, name, image_path, mirror=False):
        super().__init__()
        self.idx    = idx
        self.mirror = mirror
        self._accent = PLAYER_ACCENT[idx]

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(18)
        if mirror:
            outer.setDirection(QHBoxLayout.Direction.RightToLeft)

        # portrait
        initials = name[0].upper() if name else "?"
        self.portrait = PortraitLabel(image_path, initials, self._accent)

        # text
        text_w = QWidget()
        text_w.setStyleSheet("background:transparent;")
        tl = QVBoxLayout(text_w)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(5)
        if mirror:
            tl.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_lbl = QLabel(name.upper())
        self.name_lbl.setStyleSheet(
            "color:#ede0c4;font-family:Georgia;font-size:15px;"
            "font-weight:bold;letter-spacing:2px;background:transparent;")

        self.status_lbl = QLabel()
        self.status_lbl.setStyleSheet(
            "font-family:'Andale Mono';font-size:9px;"
            "letter-spacing:2px;background:transparent;")

        # stats row
        stats_w = QWidget()
        stats_w.setStyleSheet("background:transparent;")
        sl = QHBoxLayout(stats_w)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(14)
        if mirror:
            sl.setDirection(QHBoxLayout.Direction.RightToLeft)

        self.terr_val  = QLabel("0")
        self.army_val  = QLabel("0")
        terr_lbl = QLabel("BÖLGE")
        army_lbl = QLabel("ORDU")
        dot = QLabel("·")

        for lbl in [self.terr_val, self.army_val]:
            lbl.setStyleSheet(
                "color:#e8d8b0;font-family:Georgia;font-size:18px;"
                "font-weight:bold;background:transparent;")
        for lbl in [terr_lbl, army_lbl]:
            lbl.setStyleSheet(
                "color:rgba(180,165,130,120);font-family:'Andale Mono';"
                "font-size:8px;letter-spacing:2px;background:transparent;")
        dot.setStyleSheet("color:rgba(180,150,60,80);font-size:12px;background:transparent;")

        b1 = QVBoxLayout(); b1.setSpacing(1)
        b1.addWidget(self.terr_val); b1.addWidget(terr_lbl)
        b2 = QVBoxLayout(); b2.setSpacing(1)
        b2.addWidget(self.army_val); b2.addWidget(army_lbl)
        sl.addLayout(b1)
        sl.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
        sl.addLayout(b2)
        sl.addStretch()

        tl.addWidget(self.name_lbl)
        tl.addWidget(self.status_lbl)
        tl.addWidget(stats_w)

        outer.addWidget(self.portrait)
        outer.addWidget(text_w, stretch=1)

        self._set_inactive()

    def _set_active(self):
        c = self._accent
        self.setStyleSheet(
            f"background-color:{c['base']};"
            f"border:1px solid {c['border']};"
            "border-radius:8px;")
        self.status_lbl.setText("◆ SIRA SENDE")
        self.status_lbl.setStyleSheet(
            "color:#f0c840;font-family:'Andale Mono';"
            "font-size:9px;letter-spacing:2px;background:transparent;")
        self.portrait._set_active()

    def _set_inactive(self):
        self.setStyleSheet(
            "background-color:rgba(255,255,255,5);"
            "border:1px solid rgba(255,255,255,12);"
            "border-radius:8px;")
        self.status_lbl.setText("◇ bekliyor")
        self.status_lbl.setStyleSheet(
            "color:rgba(180,180,180,80);font-family:'Andale Mono';"
            "font-size:9px;letter-spacing:2px;background:transparent;")
        self.portrait._set_inactive()

    def set_active(self, active):
        self._set_active() if active else self._set_inactive()
        # scale portrait
        anim = QPropertyAnimation(self.portrait, b"geometry")
        anim.setDuration(350)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        r = self.portrait.geometry()
        cx, cy = r.center().x(), r.center().y()
        s = self.portrait._size
        new_s = int(s * (self.SCALE_BIG if active else self.SCALE_NORM))
        anim.setEndValue(
            self.portrait.geometry().__class__(
                cx - new_s//2, cy - new_s//2, new_s, new_s))
        anim.start()
        self._anim = anim

    def update_stats(self, territories, armies):
        self.terr_val.setText(str(territories))
        self.army_val.setText(str(armies))


class PlayerHUD(QWidget):
    PHASES = ["TAKVİYE", "SALDIRI", "HAREKET"]
    BG_COLORS = [
        ("rgba(160,30,20,0.26)", "rgba(8,18,50,0.98)"),
        ("rgba(8,18,50,0.98)",   "rgba(25,60,165,0.26)"),
    ]

    def __init__(self, player_names=("Oyuncu 1","Oyuncu 2"),
                 image_paths=("",""), current_turn=0):
        super().__init__()
        self.player_names  = list(player_names)
        self.image_paths   = list(image_paths)
        self.current_turn  = current_turn
        self.turn_number   = 1
        self.current_phase = 0
        self.setFixedHeight(114)
        self.setStyleSheet("background:transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)

        # ── main strip ──
        self.strip = QFrame()
        self.strip.setFixedHeight(88)
        sl = QHBoxLayout(self.strip)
        sl.setContentsMargins(0,0,0,0)
        sl.setSpacing(0)

        self.card0 = PlayerCard(0, player_names[0], image_paths[0], mirror=False)
        self.card1 = PlayerCard(1, player_names[1], image_paths[1], mirror=True)

        # centre VS + turn
        centre = QWidget()
        centre.setFixedWidth(88)
        centre.setStyleSheet("background:transparent;")
        cl = QVBoxLayout(centre)
        cl.setContentsMargins(0,0,0,0)
        cl.setSpacing(5)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vs = QLabel("VS")
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setStyleSheet(
            "color:rgba(180,140,50,0.5);font-family:Georgia;"
            "font-size:22px;font-weight:bold;letter-spacing:3px;"
            "background:transparent;")

        self.turn_lbl = QLabel("1")
        self.turn_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_lbl.setFixedSize(52, 22)
        self.turn_lbl.setStyleSheet(
            "color:#c8a840;font-family:'Andale Mono';font-size:9px;"
            "letter-spacing:2px;background:rgba(5,12,35,180);"
            "border:1px solid rgba(180,140,50,80);border-radius:11px;")

        cl.addWidget(vs)
        cl.addWidget(self.turn_lbl, 0, Qt.AlignmentFlag.AlignHCenter)

        sl.addWidget(self.card0, stretch=1)
        sl.addWidget(centre)
        sl.addWidget(self.card1, stretch=1)

        # ── phase bar ──
        phase_w = QWidget()
        phase_w.setFixedHeight(26)
        phase_w.setStyleSheet("background:rgba(5,10,30,250);border-top:1px solid rgba(180,140,50,40);")
        pl = QHBoxLayout(phase_w)
        pl.setContentsMargins(0,0,0,0)
        pl.setSpacing(0)
        pl.addStretch()
        self._phase_lbls = []
        for i, ph in enumerate(self.PHASES):
            lbl = QLabel(ph)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._phase_lbls.append(lbl)
            pl.addWidget(lbl)
            if i < len(self.PHASES)-1:
                sep = QLabel("  ›  ")
                sep.setStyleSheet("color:rgba(180,160,120,40);font-size:9px;background:transparent;")
                pl.addWidget(sep)
        pl.addStretch()

        root.addWidget(self.strip)
        root.addWidget(phase_w)
        self._refresh()

    def _refresh(self):
        l, r = self.BG_COLORS[self.current_turn]
        self.strip.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {l},stop:0.4 rgba(8,18,50,0.98),"
            f"stop:0.6 rgba(8,18,50,0.98),stop:1 {r});"
            "border-bottom:1px solid rgba(180,140,50,40);")
        self.card0.set_active(self.current_turn == 0)
        self.card1.set_active(self.current_turn == 1)
        self.turn_lbl.setText(f"  TUR {self.turn_number}  ")
        for i, lbl in enumerate(self._phase_lbls):
            if i == self.current_phase:
                lbl.setStyleSheet(
                    "color:#c8a840;font-family:'Andale Mono';font-size:9px;"
                    "letter-spacing:2px;background:transparent;padding:0 10px;font-weight:bold;")
            else:
                lbl.setStyleSheet(
                    "color:rgba(180,160,120,60);font-family:'Andale Mono';font-size:9px;"
                    "letter-spacing:2px;background:transparent;padding:0 10px;")

    def set_turn(self, player_idx):
        self.current_turn = player_idx
        self._refresh()

    def next_turn(self):
        self.current_turn = (self.current_turn+1) % 2
        if self.current_turn == 0:
            self.turn_number += 1
        self.current_phase = 0
        self._refresh()

    def next_phase(self):
        if self.current_phase < len(self.PHASES)-1:
            self.current_phase += 1
        else:
            self.next_turn()
        self._refresh()

    def set_player_icon(self, player_idx, image_path):
        card = self.card0 if player_idx == 0 else self.card1
        accent = PLAYER_ACCENT[player_idx]
        initials = self.player_names[player_idx][0].upper()
        new_p = PortraitLabel(image_path, initials, accent)
        layout = card.layout()
        layout.replaceWidget(card.portrait, new_p)
        card.portrait.deleteLater()
        card.portrait = new_p

    def update_stats(self, player_idx, territories, armies):
        card = self.card0 if player_idx == 0 else self.card1
        card.update_stats(territories, armies)



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
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
import os

PLAYER_ACCENT = [
    {"base": "rgba(200,50,40,0.28)",  "border": "rgba(220,70,55,0.7)",  "glow": "#dc3c37"},
    {"base": "rgba(30,70,175,0.28)",  "border": "rgba(70,130,230,0.7)", "glow": "#4682dc"},
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


# ─────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────
class MapWindow(QMainWindow):
    def __init__(self, player_names=("Oyuncu 1", "Oyuncu 2"),
                 image_paths=("", "")):
        super().__init__()
        self.setWindowTitle("Risk — Dünya Haritası")
        self.resize(1200, 740)
        self.setStyleSheet("background-color: #0a1e46;")

        central = QWidget()
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # ── HUD (top bar) ──
        self.hud = PlayerHUD(player_names=player_names,
                             image_paths=image_paths, current_turn=0)
        vbox.addWidget(self.hud)

        # ── divider ──
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(200, 160, 50, 80);")
        vbox.addWidget(div)

        # ── map ──
        self.map_view = GameMapView()
        vbox.addWidget(self.map_view, stretch=1)

        self.setCentralWidget(central)

        self.map_view.fitInView(
            self.map_view.scene_map.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # image_paths: ./images/chars/ klasöründeki dosya yolları
    win = MapWindow(
        player_names=("hanndes", "Rakip"),
        image_paths=("./images/chars/c1.png", "./images/chars/c2.png")
    )
    win.show()
    sys.exit(app.exec())