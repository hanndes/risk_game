class MessageTypes:
    SIGN_UP = "SIGN_UP"  # Oyuncu kendini tanıtırken
    CONNECTION_INFO = "CONN_INFO"  # Sunucu rakipleri eşleştirirken
    GAME_START = "GAME_START"
    ERROR = "ERROR"  # Bir hata oluştuğunda
    OPPONENT_LEFT = "OPPONENT_LEFT"
    DISCONNECT = "DISCONNECT"

# SVG haritasındaki ID'lerle tam uyumlu komşuluk (Adjacency) sözlüğü
REGION_NEIGHBORS = {
    # --- KUZEY AMERİKA ---
    "alaska": ["northwest_territory", "alberta", "kamchatka"],
    "northwest_territory": ["alaska", "alberta", "ontario", "greenland"],
    "greenland": ["northwest_territory", "ontario", "quebec", "iceland"],
    "alberta": ["alaska", "northwest_territory", "ontario", "western_united_states"],
    "ontario": ["northwest_territory", "greenland", "quebec", "alberta", "western_united_states", "eastern_united_states"],
    "quebec": ["greenland", "ontario", "eastern_united_states"],
    "western_united_states": ["alberta", "ontario", "eastern_united_states", "central_america"],
    "eastern_united_states": ["ontario", "quebec", "western_united_states", "central_america"],
    "central_america": ["western_united_states", "eastern_united_states", "venezuela"],

    # --- GÜNEY AMERİKA ---
    "venezuela": ["central_america", "peru", "brazil"],
    "peru": ["venezuela", "brazil", "argentina"],
    "brazil": ["venezuela", "peru", "argentina", "north_africa"],
    "argentina": ["peru", "brazil"],

    # --- AVRUPA ---
    "iceland": ["greenland", "scandinavia", "great_britain"],
    "scandinavia": ["iceland", "great_britain", "northern_europe", "ukraine"],
    "great_britain": ["iceland", "scandinavia", "northern_europe", "western_europe"],
    "northern_europe": ["scandinavia", "great_britain", "western_europe", "southern_europe", "ukraine"],
    "western_europe": ["great_britain", "northern_europe", "southern_europe", "north_africa"],
    "southern_europe": ["western_europe", "northern_europe", "ukraine", "middle_east", "north_africa", "egypt"],
    "ukraine": ["scandinavia", "northern_europe", "southern_europe", "ural", "afghanistan", "middle_east"],

    # --- AFRİKA ---
    "north_africa": ["brazil", "western_europe", "southern_europe", "egypt", "east_africa", "congo"],
    "egypt": ["southern_europe", "middle_east", "north_africa", "east_africa"],
    "east_africa": ["egypt", "middle_east", "north_africa", "congo", "madagascar", "south_africa"],
    "congo": ["north_africa", "east_africa", "south_africa"],
    "south_africa": ["congo", "east_africa", "madagascar"],
    "madagascar": ["east_africa", "south_africa"],

    # --- ASYA ---
    "ural": ["ukraine", "siberia", "afghanistan", "china"],
    "siberia": ["ural", "yakursk", "irkutsk", "mongolia", "china"],
    "yakursk": ["siberia", "kamchatka", "irkutsk"], # SVG'deki yazım hatasına (yakursk) göre ayarlandı
    "kamchatka": ["yakursk", "irkutsk", "mongolia", "japan", "alaska"],
    "irkutsk": ["siberia", "yakursk", "kamchatka", "mongolia"],
    "afghanistan": ["ukraine", "ural", "china", "india", "middle_east"],
    "china": ["ural", "siberia", "mongolia", "afghanistan", "india", "siam"],
    "mongolia": ["siberia", "irkutsk", "kamchatka", "japan", "china"],
    "japan": ["kamchatka", "mongolia"],
    "middle_east": ["southern_europe", "ukraine", "afghanistan", "india", "egypt", "east_africa"],
    "india": ["middle_east", "afghanistan", "china", "siam"],
    "siam": ["china", "india", "indonesia"],

    # --- AVUSTRALYA ---
    "indonesia": ["siam", "new_guinea", "western_australia"],
    "new_guinea": ["indonesia", "eastern_australia", "western_australia"],
    "western_australia": ["indonesia", "new_guinea", "eastern_australia"],
    "eastern_australia": ["new_guinea", "western_australia"]
}