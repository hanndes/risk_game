import random
import sys
import os

from shared.constants import REGION_NEIGHBORS
from shared.game_state import GameState


class RiskGameLogic:
    def __init__(self):
        self.state = GameState()
        self.setup_initial_board()

    def setup_initial_board(self):

        regions = list(REGION_NEIGHBORS.keys())
        random.shuffle(regions)

        p1_regions = regions[:21]
        p2_regions = regions[21:]

        for r in p1_regions:
            self.state.update_region(r, "player1", 1)
        for r in p2_regions:
            self.state.update_region(r, "player2", 1)

        self.state.unplaced_troops = {"player1": 19, "player2": 19}

        self.state.current_player = "player1"
        self.state.phase = "DRAFT"
        self.state.last_log = "Oyun başladı! Bölgeler rastgele dağıtıldı. Sıra Player 1'de."

    def process_action(self, client_id, action_data):
        if self.state.current_player != client_id:
            return False, "Sıra sizde değil!"

        action_type = action_data.get("action")

            # 1. Faz: Takviye
        if action_type == "DRAFT" and self.state.phase == "DRAFT":
            return self._handle_draft(client_id, action_data)

            # 2. Faz: Saldırı
        elif action_type == "ATTACK" and self.state.phase == "ATTACK":
            return self._handle_attack(client_id, action_data)

            # 3. Faz: Kuvvetleri Taşıma (Tahkimat)
        elif action_type == "FORTIFY" and self.state.phase == "FORTIFY":
            return self._handle_fortify(client_id, action_data)

            # Faz Geçişleri (Oyuncu arayüzdeki "Saldırıya Geç" butonuna basınca)
        elif action_type == "NEXT_PHASE":
            return self._advance_phase()

        elif action_type == "END_TURN":
            self._pass_turn()
            return True, "Sıra diğer oyuncuya geçti."

        return False, "Bilinmeyen hamle veya yanlış oyun fazı."

    def _handle_draft(self, player_id, data):
        region = data["region"]

        if self.state.regions[region]["owner"] != player_id:
            return False, "Sadece kendi bölgelerinize asker yerleştirebilirsiniz."

        if self.state.unplaced_troops[player_id] <= 0:
            return False, "Yerleştirilecek yedek askeriniz kalmadı."

        self.state.regions[region]["troops"] += 1
        self.state.unplaced_troops[player_id] -= 1

        self.state.last_log = f"{player_id}, {region} bölgesine 1 asker takviye etti."
        return True, "Takviye başarılı."

    def _handle_attack(self, data):
        from_region = data["from"]
        to_region = data["to"]

        attacker_troops = self.state.regions[from_region]["troops"]

        if to_region not in REGION_NEIGHBORS.get(from_region, []):
            return False, "Sadece komşu bölgelere saldırabilirsiniz!"

        if attacker_troops < 2:
            return False, "Saldırmak için yeterli askeriniz yok."
        #zar mantığı eklencek
        self.state.regions[to_region]["owner"] = self.state.current_player
        self.state.regions[to_region]["troops"] = attacker_troops - 1
        self.state.regions[from_region]["troops"] = 1

        self.state.last_log = f"{from_region}, {to_region} bölgesini ele geçirdi!"

        return True, "Saldırı başarılı!"

    def _pass_turn(self):
        if self.state.current_player == "player1":
            self.state.current_player = "player2"
        else:
            self.state.current_player = "player1"

        self.state.phase = "DRAFT"
        self.state.turn += 1