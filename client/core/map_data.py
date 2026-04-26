# Risk bölgelerinin isimleri, komşulukları ve kıta bilgileri
# SADECE SAF VERI - HIÇBIR UI KÜTÜPHANESI YOK!
from PyQt6.QtGui import QColor

# ─────────────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────────────
PALETTE = {
    "north_america": {"base": (52, 120, 180),  "light": (90, 160, 220),  "dark": (25, 75, 130)},
    "south_america": {"base": (195, 100, 30),  "light": (235, 140, 60),  "dark": (140, 65, 10)},
    "europe":        {"base": (140, 100, 210), "light": (175, 140, 245), "dark": (90, 55, 155)},
    "africa":        {"base": (155, 120, 65),  "light": (195, 160, 100), "dark": (105, 75, 30)},
    "asia":          {"base": (55, 145, 65),   "light": (90, 185, 100),  "dark": (25, 95, 35)},
    "australia":     {"base": (205, 155, 40),  "light": (245, 195, 75),  "dark": (155, 110, 10)},
}

OCEAN_DEEP   = (15,  45,  90)
OCEAN_MID    = (25,  70,  135)
BORDER_DARK  = (10,  10,  10)
BORDER_SEL   = (255, 230, 0)
CONN_COLOR   = (180, 220, 255, 60) # RGBA

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