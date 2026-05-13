import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QMainWindow, QApplication, QMessageBox,
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QSpinBox, QPushButton, QWidget)
from PyQt6.QtCore import pyqtSignal, Qt
from ui.py_ui.ui_game_window import Ui_GameWindow
from core.player import Player
from ui.widgets.dialog.occupy_dialog import OccupyDialog
from ui.widgets.map_widget import UIMap
from ui.widgets.dialog.troop_selection_dialog import TroopSelectionDialog
import os


class GameWindow(QMainWindow):

    battle_result_signal = pyqtSignal(dict)

    def __init__(self, player_obj:Player, opp_name="Bekleniyor...", opp_img=None):
        super().__init__()

        self.player_obj = player_obj

        self.ui = Ui_GameWindow()
        self.ui.setupUi(self)
        self.last_known_phase = None

        self.map_widget = UIMap()
        self.ui.map_vbox.addWidget(self.map_widget)

        self.my_player_id = player_obj.id if hasattr(player_obj, 'id') else "player1"

        if player_obj:
            self.setWindowTitle(f"Risk - Komutan: {player_obj.name} vs {opp_name}")
            self.ui.label_player_name.setText(player_obj.name)
            self.ui.label_opponent_name.setText(opp_name)

        self.ui.btn_reinforce.clicked.connect(self.on_reinforce_clicked)
        self.ui.btn_end_turn.clicked.connect(self.on_end_turn_clicked)
        self.ui.btn_attack.clicked.connect(self.on_attack_clicked)
        self.ui.btn_roll_dice.clicked.connect(self.on_roll_dice_clicked)
        self.ui.btn_fortify.clicked.connect(self.on_fortify_clicked)

        self.battle_result_signal.connect(self.handle_battle_result)

    def update_ui_with_state(self, state):

        self.current_state = state
        print(">>> UI GÜNCELLEME TETİKLENDİ: Veriler kutulara yazılıyor...")

        if hasattr(self, 'last_known_phase') and self.last_known_phase != state.phase:

            if hasattr(self.map_widget, 'clear_selection'):
                self.map_widget.clear_selection()

            self.map_widget.selected_region = None
            self.map_widget.target_region = None

        self.last_known_phase = state.phase

        phase_map = {
            "DRAFT": "TAKVİYE",
            "ATTACK": "SALDIRI",
            "FORTIFY": "KUVVETLERİ TAŞI"
        }

        display_phase = phase_map.get(state.phase, state.phase)

        att_dice = getattr(state, 'prep_att_dice', 0)
        def_dice = getattr(state, 'prep_def_dice', 0)

        # --- ZAR ALANI DİNAMİK YÖNETİMİ ---
        if hasattr(self.ui, 'dice_container'):
            if state.phase == "ATTACK":
                self.ui.dice_container.show()
                self._clear_dice_layout()

                # SIRA BENDEYSE
                if state.current_player == self.my_player_id:
                    if att_dice > 0:
                        self._draw_dice(att_dice, "#ff6644")

                    self.ui.btn_roll_dice.setEnabled(att_dice > 0)

                # SIRA RAKİPTEYSE (SAVUNAN TARAF BENİM)
                else:
                    if def_dice > 0:
                        self._draw_dice(def_dice, "#4488cc")

                    self.ui.btn_roll_dice.setEnabled(False)
            else:
                self.ui.dice_container.hide()

        # --- OYUNCU TUR VE BUTON KONTROLLERİ ---
        if state.current_player == self.my_player_id:
            self.ui.label_turn_indicator.setText("SENİN TURUN")
            self.ui.label_turn_indicator.setStyleSheet(
                "background-color: #44cc44; color: #ffffff; padding: 3px 10px; border-radius: 3px;")  # Yeşil renk
            self.ui.label_phase.setText(f"FAZ: {display_phase}")

            self.ui.btn_reinforce.setEnabled(state.phase == "DRAFT")
            self.ui.btn_fortify.setEnabled(state.phase == "FORTIFY")
            self.ui.btn_end_turn.setEnabled(True)

            if state.phase == "ATTACK":
                if att_dice > 0:
                    self.ui.btn_attack.setEnabled(False)
                    self.ui.btn_roll_dice.setEnabled(True)
                else:
                    self.ui.btn_attack.setEnabled(True)
                    self.ui.btn_roll_dice.setEnabled(False)
            else:
                self.ui.btn_attack.setEnabled(False)
                self.ui.btn_roll_dice.setEnabled(False)

            my_leftover = state.unplaced_troops.get(self.my_player_id, 0)
            if state.phase == "DRAFT":
                self.ui.btn_end_turn.setText("SALDIRIYA GEÇ")
                self.ui.btn_end_turn.setEnabled(my_leftover == 0)
            elif state.phase == "ATTACK":
                self.ui.btn_end_turn.setText("TAHKİMATA GEÇ")
            elif state.phase == "FORTIFY":
                self.ui.btn_end_turn.setText("TURU BİTİR")

        else:
            self.ui.label_turn_indicator.setText("RAKİBİN TURU")
            self.ui.label_turn_indicator.setStyleSheet(
                "background-color: #8b1a1a; color: #ffffff; padding: 3px 10px; border-radius: 3px;")  # Kırmızı renk
            self.ui.label_phase.setText(f"Sıradaki: {display_phase}")

            self.ui.btn_reinforce.setEnabled(False)
            self.ui.btn_attack.setEnabled(False)
            self.ui.btn_fortify.setEnabled(False)
            self.ui.btn_end_turn.setEnabled(False)

        # --- HARİTA VE BÖLGE GÜNCELLEMELERİ ---
        my_region_count = 0
        opp_region_count = 0
        total_regions = len(state.regions) if len(state.regions) > 0 else 42

        for region_id, region_data in state.regions.items():
            owner = region_data["owner"]
            troops = region_data["troops"]

            if owner == self.my_player_id:
                my_region_count += 1
                display_owner = "player1"
            else:
                opp_region_count += 1
                display_owner = "player2"

            is_source = (region_id == getattr(self.map_widget, 'selected_region', None))
            is_target = (region_id == getattr(self.map_widget, 'target_region', None))

            if (is_source or is_target) and state.phase == "ATTACK" and att_dice > 0:
                pass
            else:
                if hasattr(self.map_widget, 'update_region_ui'):
                    self.map_widget.update_region_ui(region_id, display_owner, troops)

        # --- İSTATİSTİKLER VE PROGRESS BAR ---
        self.ui.label_territories_value.setText(f"{my_region_count} / {total_regions}")
        self.ui.label_opponent_territories_value.setText(f"{opp_region_count} / {total_regions}")

        if total_regions > 0:
            percentage = int((my_region_count / total_regions) * 100)
            self.ui.progress_bar.setValue(percentage)

        if hasattr(state, "turn"):
            self.ui.label_round_value.setText(str(state.turn))

        # --- LOG FİLTRELEME ---
        if hasattr(state, "last_log") and state.last_log:
            is_dice_log = "Zarlar" in state.last_log or "A:[" in state.last_log

            if not is_dice_log:
                self.ui.log_box.append(f"Karargah: {state.last_log}")
            else:
                print(f">>> UI Log Filtrelendi (Zar Sonucu): {state.last_log}")

        # --- ASKER SAYILARI ---
        my_leftover = state.unplaced_troops.get(self.my_player_id, 0)
        self.ui.label_troops_value.setText(str(my_leftover))

        opp_id = "player2" if self.my_player_id == "player1" else "player1"
        opp_leftover = state.unplaced_troops.get(opp_id, 0)
        self.ui.label_opponent_troops_value.setText(str(opp_leftover))

    # --- BUTON TIKLAMA FONKSİYONLARI ---
    def on_reinforce_clicked(self):

        selected_region = getattr(self.map_widget, 'selected_region', None)

        if not selected_region:
            QMessageBox.warning(self, "Komutanım!", "Lütfen haritadan takviye göndermek istediğiniz bölgeyi seçin.")
            return

        my_leftover = int(self.ui.label_troops_value.text())
        if my_leftover <= 0:
            QMessageBox.information(self, "Bilgi", "Gönderilecek yedek askeriniz kalmadı.")
            return

        dialog = TroopSelectionDialog(selected_region, my_leftover, self)

        if dialog.exec():
            amount = dialog.get_value()

            action_data = {
                "action": "DRAFT",
                "region": selected_region,
                "amount": amount
            }

            print(f">>> Sunucuya İstek Paketleniyor: {action_data}")

            try:
                if self.player_obj:
                    self.player_obj.send_action(action_data)
                else:
                    print("HATA: Player objesi bulunamadı!")
            except Exception as e:
                QMessageBox.critical(self, "Bağlantı Hatası", f"Sunucuya veri gönderilirken hata oluştu:\n{e}")

            print(f">>> Sunucuya İstek: {action_data}")

    def on_end_turn_clicked(self):

        btn_text = self.ui.btn_end_turn.text()

        if "TURU BİTİR" in btn_text:
            action = "END_TURN"
        else:
            action = "NEXT_PHASE"

        action_data = {"action": action}

        try:
            if self.player_obj:
                self.player_obj.send_action(action_data)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sunucu ile iletişim kurulamadı: {e}")

    def on_attack_clicked(self):
        source_region = getattr(self.map_widget, 'selected_region', None)
        target_region = getattr(self.map_widget, 'target_region', None)

        if not source_region or not target_region:
            QMessageBox.warning(self, "Komutanım!",
                                "Saldırmak için önce KENDİ bölgenizi, ardından DÜŞMAN bölgesini seçmelisiniz.")
            return

        if not hasattr(self, 'current_state'):
            return

        source_owner = self.current_state.regions[source_region]["owner"]
        target_owner = self.current_state.regions[target_region]["owner"]

        if source_owner != self.my_player_id or target_owner == self.my_player_id:
            QMessageBox.warning(self, "Hatalı Seçim!",
                                "Lütfen saldırmak için KENDİ bölgenizi ve bir DÜŞMAN bölgesi seçin!")

            if hasattr(self.map_widget, 'clear_selection'):
                self.map_widget.clear_selection()

            self.map_widget.selected_region = None
            self.map_widget.target_region = None

            if hasattr(self.map_widget, 'update'):
                self.map_widget.update()
            return

        source_troops = self.current_state.regions[source_region]["troops"]
        if source_troops < 2:
            QMessageBox.warning(self, "Yetersiz Birlik",
                                "Saldırı başlatabilmek için bölgede en az 2 askeriniz olmalıdır.")
            return

        action_data = {
            "action": "PREPARE_ATTACK",
            "from": source_region,
            "to": target_region
        }

        try:
            if self.player_obj:
                self.player_obj.send_action(action_data)
                self.ui.btn_attack.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sunucuya veri gönderilemedi: {e}")

    def _draw_dice(self, dice_count, border_color):
        h_box = QHBoxLayout()
        h_box.setSpacing(10)
        h_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(current_dir, "..", "..", "client", "assets", "images", "dice.png")

        for _ in range(dice_count):
            lbl = QLabel()
            lbl.setFixedSize(60, 60)
            px = QPixmap(img_path)
            if not px.isNull():
                lbl.setPixmap(px)
                lbl.setScaledContents(True)
                lbl.setStyleSheet(f"border: 2px solid {border_color}; border-radius: 5px;")
            h_box.addWidget(lbl)

        temp_widget = QWidget()
        temp_widget.setLayout(h_box)
        self.ui.dice_layout.addWidget(temp_widget)

    def _clear_dice_layout(self):
        while self.ui.dice_layout.count():
            item = self.ui.dice_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def on_roll_dice_clicked(self):
        source_region = getattr(self.map_widget, 'selected_region', None)
        target_region = getattr(self.map_widget, 'target_region', None)

        if not source_region or not target_region:
            return

        action_data = {
            "action": "ATTACK",
            "from": source_region,
            "to": target_region
        }

        print(f">>> Sunucuya Saldırı İsteği Gönderiliyor: {action_data}")

        try:
            if self.player_obj:
                self.player_obj.send_action(action_data)

                self.ui.btn_roll_dice.setEnabled(False)
                self._clear_dice_layout()

                info = QLabel("Savaş Bekleniyor...")
                info.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info.setStyleSheet("color:#555555; font-style:italic;")
                self.ui.dice_layout.addWidget(info)

                if hasattr(self.map_widget, 'clear_selection'):
                    self.map_widget.clear_selection()

                self.map_widget.selected_region = None
                self.map_widget.target_region = None

                if hasattr(self.map_widget, 'update'):
                    self.map_widget.update()

        except Exception as e:
            QMessageBox.critical(self, "Bağlantı Hatası", f"Sunucuya veri gönderilirken hata oluştu:\n{e}")

    def on_fortify_clicked(self):

        source_region = getattr(self.map_widget, 'selected_region', None)
        target_region = getattr(self.map_widget, 'target_region', None)

        if not source_region or not target_region:
            QMessageBox.warning(self, "Komutanım!",
                                "Kuvvet taşımak için haritadan önce KAYNAK bölgenizi, sonra HEDEF bölgenizi seçmelisiniz.")
            return

        if not hasattr(self, 'current_state'):
            return

        source_owner = self.current_state.regions[source_region]["owner"]
        target_owner = self.current_state.regions[target_region]["owner"]

        if source_owner != self.my_player_id or target_owner != self.my_player_id:
            QMessageBox.warning(self, "Hatalı Seçim!",
                                "Kuvvet taşıması sadece KENDİ bölgeleriniz arasında yapılabilir!")
            return

        source_troops = self.current_state.regions[source_region]["troops"]

        if source_troops < 2:
            QMessageBox.warning(self, "Yetersiz Birlik",
                                "Bu bölgeden asker taşıyamazsınız. Sınır güvenliği için en az 1 asker kalmalıdır.")
            return

        max_transferable = source_troops - 1

        dialog = TroopSelectionDialog(source_region, max_transferable, self)

        if dialog.exec():
            amount = dialog.get_value()

            action_data = {
                "action": "FORTIFY",
                "from": source_region,
                "to": target_region,
                "amount": amount
            }

            print(f">>> Sunucuya Tahkimat İsteği Gönderiliyor: {action_data}")

            try:
                if self.player_obj:
                    self.player_obj.send_action(action_data)

                    if hasattr(self.map_widget, 'clear_selection'):
                        self.map_widget.clear_selection()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Sunucuya veri gönderilemedi: {e}")

    def handle_battle_result(self, result_data):
        status = result_data.get("status")
        from_reg = result_data.get("from")
        to_reg = result_data.get("to")
        max_transferable = result_data.get("max_transferable", 0)

        if self.current_state.current_player != self.my_player_id:
            print(f">>> Bilgi: Savunmadayız. {from_reg} üzerinden {to_reg} bölgesine saldırıldı. Sonuç bekleniyor.")
            return

        if status != "ATTACKER_WON":
            print(f">>> Bilgi: Zar atıldı ancak bölge henüz düşmedi. Mevcut savaş durumu: {status}")
            return  # Savaş devam ediyor, popup açma

        if max_transferable > 0:
            dialog = OccupyDialog(from_reg, to_reg, max_transferable, self)

            if dialog.exec():
                amount = dialog.get_value()

                occupy_action = {
                    "action": "OCCUPY",
                    "from": from_reg,
                    "to": to_reg,
                    "amount": amount
                }

                try:
                    self.player_obj.send_action(occupy_action)
                    print(f">>> İşgal Başlatıldı: {from_reg} -> {to_reg} ({amount} asker)")
                except Exception as e:
                    print(f"HATA: İşgal verisi gönderilemedi: {e}")
        else:

            print(f">>> Bilgi: {from_reg} bölgesinde sadece sınır güvenliği için 1 asker kaldığından, ekstra sevkiyat yapılamadı. Saldırı birliği {to_reg} bölgesine yerleşti")

    def closeEvent(self, event):

        if hasattr(self, 'player_obj') and self.player_obj and hasattr(self.player_obj, 'client'):
            if self.player_obj.client.client_socket:
                self.player_obj.client.send_disconnect_message()
                self.player_obj.client.close_connection()

        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_player = Player("Komutanı")

    window = GameWindow(test_player, opp_name="Komutan Hande")
    window.show()

    sys.exit(app.exec())