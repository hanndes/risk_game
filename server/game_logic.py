import random
import sys
import os

from shared.constants import REGION_NEIGHBORS, MessageTypes
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

        if action_type == MessageTypes.DISCONNECT:
            return True, None

            # 1. Faz: Takviye
        if action_type == "DRAFT" and self.state.phase == "DRAFT":
            return self._handle_draft(client_id, action_data)

        elif action_type == "PREPARE_ATTACK" and self.state.phase == "ATTACK":
            return self._handle_prepare_attack(client_id, action_data)

            # 2. Faz: Saldırı
        elif action_type == "ATTACK" and self.state.phase == "ATTACK":
            return self._handle_attack(client_id, action_data)

        elif action_type == "OCCUPY" and self.state.phase == "ATTACK":
            return self._handle_occupy(client_id, action_data)

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
        amount = data.get("amount", 1)

        if self.state.regions[region]["owner"] != player_id:
            return False, "Sadece kendi bölgelerinize asker yerleştirebilirsiniz."

        if self.state.unplaced_troops[player_id] < amount:
            return False, f"Yeterli yedek askeriniz yok. Kalan: {self.state.unplaced_troops[player_id]}"

        self.state.regions[region]["troops"] += amount
        self.state.unplaced_troops[player_id] -= amount

        self.state.last_log = f"{player_id}, {region} bölgesine {amount} asker takviye etti."

        if self.state.unplaced_troops[player_id] == 0:
            self.state.phase = "ATTACK"
            self.state.last_log += " Askerler tükendi. SALDIRI fazı başladı!"

        return True, "Takviye başarılı."

    def _handle_attack(self, client_id, data):
        from_region = data["from"]
        to_region = data["to"]

        attacker_total = self.state.regions[from_region]["troops"]
        defender_owner = self.state.regions[to_region]["owner"]
        defender_total = self.state.regions[to_region]["troops"]

        if to_region not in REGION_NEIGHBORS.get(from_region, []):
            return False, "Sadece komşu bölgelere saldırabilirsiniz!"

        if attacker_total < 2:
            return False, "Saldırmak için yeterli askeriniz yok."

        att_dice_count = min(3, attacker_total - 1)
        def_dice_count = min(2, defender_total)

        self.state.last_attack_dice_count = def_dice_count

        final_att_rolls = sorted([random.randint(1, 6) for _ in range(att_dice_count)], reverse=True)
        final_def_rolls = sorted([random.randint(1, 6) for _ in range(def_dice_count)], reverse=True)

        att_losses = 0
        def_losses = 0

        for a, d in zip(final_att_rolls, final_def_rolls):
            if a > d:
                def_losses += 1
                self.state.regions[to_region]["troops"] -= 1
            else:
                att_losses += 1
                self.state.regions[from_region]["troops"] -= 1

        battle_status = "ONGOING"
        extra_transferable = 0

        if self.state.regions[to_region]["troops"] <= 0:
            self.state.regions[to_region]["owner"] = client_id

            surviving_troops = att_dice_count - att_losses
            self.state.regions[to_region]["troops"] = surviving_troops
            self.state.regions[from_region]["troops"] -= surviving_troops

            battle_status = "ATTACKER_WON"
            self.state.last_log = f"{client_id}, {to_region} bölgesini ele geçirdi! Zarlar -> A:{final_att_rolls} S:{final_def_rolls}"

            extra_transferable = self.state.regions[from_region]["troops"] - 1

        else:
            self.state.last_log = f"Çatışma! Zarlar: A:{final_att_rolls} S:{final_def_rolls}. Kayıplar: Saldıran -{att_losses}, Savunan -{def_losses}."

        print(f"\n[SAVAŞ RAPORU] {from_region} -> {to_region}")
        print(f"Saldıran Zarları: {final_att_rolls}")
        print(f"Savunan Zarları : {final_def_rolls}")
        print(f"Kayıplar: Saldıran -{att_losses} | Savunan -{def_losses}")
        print("-" * 40)

        dice_event = {
            "type": "BATTLE_RESULT",
            "att_rolls": final_att_rolls,
            "def_rolls": final_def_rolls,
            "from": from_region,
            "to": to_region,
            "status": battle_status,
            "att_loss": att_losses,
            "def_loss": def_losses,
            "max_transferable": extra_transferable
        }

        self.state.prep_att_dice = 0
        self.state.prep_def_dice = 0

        return True, dice_event

    def _handle_occupy(self, client_id, data):
        from_region = data["from"]
        to_region = data["to"]
        amount = data["amount"]

        if self.state.regions[from_region]["owner"] != client_id or self.state.regions[to_region]["owner"] != client_id:
            return False, "Bölgeler size ait değil."

        if self.state.regions[from_region]["troops"] <= amount:
            return False, "Bu kadar asker kaydıramazsınız (En az 1 asker kalmalı)."

        self.state.regions[from_region]["troops"] -= amount
        self.state.regions[to_region]["troops"] += amount
        self.state.last_log = f"{client_id}, işgal edilen {to_region} bölgesine {amount} asker daha gönderdi."

        return True, "İşgal kuvvetleri başarıyla yerleşti."

    def _handle_prepare_attack(self, client_id, data):
        from_region = data["from"]
        to_region = data["to"]

        attacker_total = self.state.regions[from_region]["troops"]
        defender_total = self.state.regions[to_region]["troops"]

        self.state.prep_att_dice = min(3, attacker_total - 1)
        self.state.prep_def_dice = min(2, defender_total)

        return True, "Saldırı hazırlığı yapıldı, zarlar ekrana yansıtılıyor."

    def _handle_fortify(self, client_id, data):

        from_region = data["from"]
        to_region = data["to"]
        amount = data["amount"]

        if self.state.regions[from_region]["owner"] != client_id or self.state.regions[to_region]["owner"] != client_id:
            return False, "Sadece kendi bölgeleriniz arasında asker taşıyabilirsiniz."

        if self.state.regions[from_region]["troops"] - amount < 1:
            return False, "Kaynak bölgede en az 1 asker bırakmak zorundasınız."

        if not self._has_valid_path(client_id, from_region, to_region):
            return False, "Bu iki bölge arasında size ait kesintisiz bir yol bulunmuyor!"

        self.state.regions[from_region]["troops"] -= amount
        self.state.regions[to_region]["troops"] += amount
        self.state.last_log = f"{client_id}, {from_region} bölgesinden {to_region} bölgesine {amount} asker kaydırdı."

        self._pass_turn()

        return True, "Kuvvetler başarıyla taşındı ve tur sona erdi."

    def _has_valid_path(self, player_id, start_region, end_region):

        if start_region == end_region:
            return True

        visited = set()
        queue = [start_region]
        visited.add(start_region)

        while queue:
            current = queue.pop(0)

            if current == end_region:
                return True

            neighbors = REGION_NEIGHBORS.get(current, [])

            for neighbor in neighbors:
                if neighbor not in visited and self.state.regions[neighbor]["owner"] == player_id:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

    def _pass_turn(self):
        if self.state.current_player == "player2":
            self.state.turn += 1
            self.state.current_player = "player1"
        else:
            self.state.current_player = "player2"

        self.state.phase = "DRAFT"
        self.state.last_log = f"Sıra {self.state.current_player}'e geçti. Tur: {self.state.turn}"

    def _advance_phase(self):
        if self.state.phase == "DRAFT":
            self.state.phase = "ATTACK"
            self.state.last_log = "Takviye atlandı, SALDIRI fazına geçildi."
        elif self.state.phase == "ATTACK":
            self.state.phase = "FORTIFY"
            self.state.last_log = "Saldırı bitti, KUVVETLERİ TAŞIMA fazına geçildi."
        elif self.state.phase == "FORTIFY":
            return True, "Sıra diğer oyuncuya geçti."

        return True, f"Faz {self.state.phase} olarak değişti."