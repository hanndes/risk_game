class GameState:
    def __init__(self):
        self.turn = 1
        self.current_player = None
        self.phase = "DRAFT"

        self.regions = {}

        self.players = {
            "player1": {"name": "Bekleniyor...", "color": "red"},
            "player2": {"name": "Bekleniyor...", "color": "blue"}
        }

        self.unplaced_troops = {
            "player1": 19,
            "player2": 19
        }

    def update_region(self, region_id, owner, troops):
        self.regions[region_id] = {"owner": owner, "troops": troops}