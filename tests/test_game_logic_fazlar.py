import pytest

from server.game_logic import RiskGameLogic
from shared.constants import MessageTypes, REGION_NEIGHBORS

P1, P2 = "player1", "player2"


# --- Yardımcılar ---

@pytest.fixture
def game():
    return RiskGameLogic()


def hepsini_ata(game, owner, troops=1):
    for r in REGION_NEIGHBORS:
        game.state.update_region(r, owner, troops)


def hazirla(game, bolgeler, faz):
    """bolgeler: {bolge: (sahip, asker)}; geri kalan player2'nin. Sıra player1'de."""
    hepsini_ata(game, P2)
    for r, (sahip, asker) in bolgeler.items():
        game.state.update_region(r, sahip, asker)
    game.state.current_player = P1
    game.state.phase = faz


# --- GER-09: Faz geçişleri (NEXT_PHASE) ---

def test_ger09_takviyeden_saldiriya_gecilir(game):
    game.state.phase = "DRAFT"
    ok, _ = game.process_action(P1, {"action": "NEXT_PHASE"})
    assert ok is True
    assert game.state.phase == "ATTACK"


def test_ger09_saldiridan_kuvvet_tasimaya_gecilir(game):
    game.state.phase = "ATTACK"
    ok, _ = game.process_action(P1, {"action": "NEXT_PHASE"})
    assert ok is True
    assert game.state.phase == "FORTIFY"


def test_ger09_son_fazda_next_phase_reddedilir_tur_gecmez(game):
    # Tur sadece END_TURN ile biter (istemci böyle çalışıyor); NEXT_PHASE turu sessizce geçirmemeli
    game.state.phase = "FORTIFY"
    ok, mesaj = game.process_action(P1, {"action": "NEXT_PHASE"})
    assert ok is False
    assert "END_TURN" in mesaj
    assert game.state.phase == "FORTIFY"
    assert game.state.current_player == P1


def test_ger09_disconnect_hamlesi_kabul_edilir(game):
    assert game.process_action(P1, {"action": MessageTypes.DISCONNECT}) == (True, None)


# --- GER-10: İşgal sonrası asker kaydırma (OCCUPY) ---

def test_ger10_isgal_edilen_bolgeye_asker_kaydirilir(game):
    hazirla(game, {"alaska": (P1, 5), "kamchatka": (P1, 1)}, "ATTACK")
    ok, _ = game.process_action(P1, {"action": "OCCUPY", "from": "alaska", "to": "kamchatka", "amount": 3})
    assert ok is True
    assert game.state.regions["alaska"]["troops"] == 2
    assert game.state.regions["kamchatka"]["troops"] == 4


def test_ger10_baska_oyuncunun_bolgesine_kaydirilamaz(game):
    hazirla(game, {"alaska": (P1, 5)}, "ATTACK")  # kamchatka player2'nin
    ok, _ = game.process_action(P1, {"action": "OCCUPY", "from": "alaska", "to": "kamchatka", "amount": 2})
    assert ok is False
    assert game.state.regions["alaska"]["troops"] == 5


def test_ger10_kaynak_bolgede_en_az_1_asker_kalmali(game):
    hazirla(game, {"alaska": (P1, 5), "kamchatka": (P1, 1)}, "ATTACK")
    ok, _ = game.process_action(P1, {"action": "OCCUPY", "from": "alaska", "to": "kamchatka", "amount": 5})
    assert ok is False
    assert game.state.regions["alaska"]["troops"] == 5


def test_ger10_negatif_miktar_reddedilmeli(game):
    hazirla(game, {"alaska": (P1, 5), "kamchatka": (P1, 1)}, "ATTACK")
    ok, _ = game.process_action(P1, {"action": "OCCUPY", "from": "alaska", "to": "kamchatka", "amount": -2})
    assert ok is False
    assert game.state.regions["alaska"]["troops"] == 5
    assert game.state.regions["kamchatka"]["troops"] == 1


# --- GER-11: Saldırı hazırlığı (PREPARE_ATTACK) ---

@pytest.mark.parametrize("saldiran, savunan, beklenen_att, beklenen_def", [
    (4, 2, 3, 2),
    (10, 5, 3, 2),   # üst sınırlar
    (3, 1, 2, 1),
    (2, 1, 1, 1),
])
def test_ger11_hazirlik_zar_sayilarini_belirler(game, saldiran, savunan, beklenen_att, beklenen_def):
    hazirla(game, {"alaska": (P1, saldiran), "kamchatka": (P2, savunan)}, "ATTACK")
    ok, _ = game.process_action(P1, {"action": "PREPARE_ATTACK", "from": "alaska", "to": "kamchatka"})
    assert ok is True
    assert game.state.prep_att_dice == beklenen_att
    assert game.state.prep_def_dice == beklenen_def


def test_ger11_rakibin_bolgesinden_hazirlik_yapilamaz(game):
    hazirla(game, {"kamchatka": (P2, 2)}, "ATTACK")  # alaska da player2'nin
    ok, _ = game.process_action(P1, {"action": "PREPARE_ATTACK", "from": "alaska", "to": "kamchatka"})
    assert ok is False


# --- GER-12: Kuvvet taşıma ek kuralları (FORTIFY) ---

def test_ger12_rakibin_bolgesine_tasima_reddedilir(game):
    hazirla(game, {"alaska": (P1, 5)}, "FORTIFY")  # alberta player2'nin
    ok, _ = game.process_action(P1, {"action": "FORTIFY", "from": "alaska", "to": "alberta", "amount": 2})
    assert ok is False
    assert game.state.regions["alaska"]["troops"] == 5
    assert game.state.current_player == P1  # reddedilen hamle turu bitirmemeli


def test_ger12_negatif_miktar_reddedilmeli(game):
    hazirla(game, {"alaska": (P1, 5), "alberta": (P1, 1)}, "FORTIFY")
    ok, _ = game.process_action(P1, {"action": "FORTIFY", "from": "alaska", "to": "alberta", "amount": -2})
    assert ok is False
    assert game.state.regions["alberta"]["troops"] == 1