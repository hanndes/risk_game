import pytest

from server.game_logic import RiskGameLogic
from shared.constants import CONTINENTS, REGION_NEIGHBORS

P1, P2 = "player1", "player2"


# --- Yardımcılar ---

@pytest.fixture
def game():
    return RiskGameLogic()


def hepsini_ata(game, owner, troops=1):
    """Haritadaki tüm bölgeleri tek oyuncuya verir (rastgele dağıtımı ezmek için)."""
    for r in REGION_NEIGHBORS:
        game.state.update_region(r, owner, troops)


def zarlari_sabitle(monkeypatch, degerler):
    """random.randint sırayla verilen değerleri döndürür: önce saldıran, sonra savunan zarları."""
    it = iter(degerler)
    monkeypatch.setattr("server.game_logic.random.randint", lambda a, b: next(it))


def saldiri_hazirla(game, from_r, to_r, saldiran_asker, savunan_asker):
    hepsini_ata(game, P2)
    game.state.update_region(from_r, P1, saldiran_asker)
    game.state.update_region(to_r, P2, savunan_asker)
    game.state.current_player = P1
    game.state.phase = "ATTACK"


def saldir(game, from_r, to_r):
    return game.process_action(P1, {"action": "ATTACK", "from": from_r, "to": to_r})


# --- GER-01: Başlangıç dağılımı ---

@pytest.mark.parametrize("deneme", range(5))  # dağıtım rastgele, birkaç kez dene
def test_ger01_bolgeler_21er_dagitilir(deneme):
    game = RiskGameLogic()
    sahipler = [d["owner"] for d in game.state.regions.values()]
    assert len(sahipler) == 42
    assert sahipler.count(P1) == 21
    assert sahipler.count(P2) == 21


def test_ger01_baslangic_durumu(game):
    assert game.state.current_player == P1
    assert game.state.phase == "DRAFT"
    assert game.state.unplaced_troops == {P1: 19, P2: 19}
    assert all(d["troops"] == 1 for d in game.state.regions.values())


# --- GER-02: Zar sayıları ve savaş kuralları ---

@pytest.mark.parametrize("saldiran, savunan, beklenen_att, beklenen_def", [
    (2, 1, 1, 1),   # en az asker: 1 zar
    (3, 1, 2, 1),
    (4, 2, 3, 2),   # saldıran en fazla 3 zar
    (10, 5, 3, 2),  # savunan en fazla 2 zar
    (2, 2, 1, 2),
])
def test_ger02_zar_sayilari(game, monkeypatch, saldiran, savunan, beklenen_att, beklenen_def):
    saldiri_hazirla(game, "alaska", "kamchatka", saldiran, savunan)
    zarlari_sabitle(monkeypatch, [3] * 5)
    ok, olay = saldir(game, "alaska", "kamchatka")
    assert ok is True
    assert len(olay["att_rolls"]) == beklenen_att
    assert len(olay["def_rolls"]) == beklenen_def


def test_ger02_saldiran_kazanir_bolgeyi_alir(game, monkeypatch):
    saldiri_hazirla(game, "alaska", "kamchatka", 4, 1)
    zarlari_sabitle(monkeypatch, [6, 6, 6, 1])
    ok, olay = saldir(game, "alaska", "kamchatka")
    assert ok is True
    assert olay["status"] == "ATTACKER_WON"
    assert game.state.regions["kamchatka"] == {"owner": P1, "troops": 3}
    assert game.state.regions["alaska"]["troops"] == 1


def test_ger02_beraberlikte_savunan_kazanir(game, monkeypatch):
    saldiri_hazirla(game, "alaska", "kamchatka", 3, 2)
    zarlari_sabitle(monkeypatch, [4, 4, 4, 4])
    _, olay = saldir(game, "alaska", "kamchatka")
    assert olay["att_loss"] == 2
    assert olay["def_loss"] == 0
    assert game.state.regions["alaska"]["troops"] == 1
    assert game.state.regions["kamchatka"]["troops"] == 2


def test_ger02_karisik_sonuc_ikisi_de_kayip_verir(game, monkeypatch):
    saldiri_hazirla(game, "alaska", "kamchatka", 4, 2)
    zarlari_sabitle(monkeypatch, [6, 1, 1, 3, 3])  # saldıran 6,1,1 - savunan 3,3
    _, olay = saldir(game, "alaska", "kamchatka")
    assert olay["status"] == "ONGOING"
    assert (olay["att_loss"], olay["def_loss"]) == (1, 1)
    assert game.state.regions["alaska"]["troops"] == 3
    assert game.state.regions["kamchatka"]["troops"] == 1


def test_ger02_tek_askerle_saldirilamaz(game):
    saldiri_hazirla(game, "alaska", "kamchatka", 1, 3)
    ok, _ = saldir(game, "alaska", "kamchatka")
    assert ok is False


def test_ger02_komsu_olmayan_bolgeye_saldirilamaz(game):
    saldiri_hazirla(game, "alaska", "japan", 5, 1)
    ok, _ = saldir(game, "alaska", "japan")
    assert ok is False


# --- GER-03: Takviye (DRAFT) ---

def kendi_bolgem(game, oyuncu=P1):
    return next(r for r, d in game.state.regions.items() if d["owner"] == oyuncu)


def test_ger03_takviye_gecerli(game):
    bolge = kendi_bolgem(game)
    ok, _ = game.process_action(P1, {"action": "DRAFT", "region": bolge, "amount": 3})
    assert ok is True
    assert game.state.regions[bolge]["troops"] == 4
    assert game.state.unplaced_troops[P1] == 16


def test_ger03_dusman_bolgesine_takviye_yapilamaz(game):
    bolge = kendi_bolgem(game, P2)
    ok, _ = game.process_action(P1, {"action": "DRAFT", "region": bolge, "amount": 1})
    assert ok is False


def test_ger03_yedek_askerden_fazlasi_yerlestirilemez(game):
    bolge = kendi_bolgem(game)
    ok, _ = game.process_action(P1, {"action": "DRAFT", "region": bolge, "amount": 20})
    assert ok is False
    assert game.state.unplaced_troops[P1] == 19


def test_ger03_askerler_bitince_saldiri_fazi_baslar(game):
    game.state.unplaced_troops[P1] = 2
    bolge = kendi_bolgem(game)
    game.process_action(P1, {"action": "DRAFT", "region": bolge, "amount": 2})
    assert game.state.phase == "ATTACK"


def test_sirasi_olmayan_oyuncu_hamle_yapamaz(game):
    bolge = kendi_bolgem(game, P2)
    ok, mesaj = game.process_action(P2, {"action": "DRAFT", "region": bolge, "amount": 1})
    assert ok is False
    assert mesaj == "Sıra sizde değil!"


def test_yanlis_fazda_hamle_reddedilir(game):
    game.state.phase = "ATTACK"
    bolge = kendi_bolgem(game)
    ok, _ = game.process_action(P1, {"action": "DRAFT", "region": bolge, "amount": 1})
    assert ok is False


# --- GER-04: Tur, takviye ve kıta bonusu ---

BONUSSUZ_12_BOLGE = ["alaska", "brazil", "iceland", "egypt", "china", "japan",
                     "indonesia", "ural", "siberia", "peru", "congo", "madagascar"]


def test_ger04_bolge_bonusu_ucte_birdir(game):
    hepsini_ata(game, P2)
    for r in BONUSSUZ_12_BOLGE:
        game.state.update_region(r, P1, 1)
    game.state.unplaced_troops[P1] = 0
    game._add_reinforcements(P1)
    assert game.state.unplaced_troops[P1] == 12 // 3  # 4


def test_ger04_bolge_bonusu_en_az_3(game):
    hepsini_ata(game, P2)
    for r in ["alaska", "brazil", "japan"]:
        game.state.update_region(r, P1, 1)
    game.state.unplaced_troops[P1] = 0
    game._add_reinforcements(P1)
    assert game.state.unplaced_troops[P1] == 3


@pytest.mark.parametrize("kita", list(CONTINENTS))
def test_ger04_kita_bonusu_tam_kitada_verilir(game, kita):
    hepsini_ata(game, P2)
    for r in CONTINENTS[kita]["regions"]:
        game.state.update_region(r, P1, 1)
    assert game._calculate_continent_bonus(P1) == CONTINENTS[kita]["bonus"]


def test_ger04_eksik_kitada_bonus_yok(game):
    hepsini_ata(game, P2)
    for r in CONTINENTS["Asia"]["regions"][:-1]:  # sonuncusu eksik
        game.state.update_region(r, P1, 1)
    assert game._calculate_continent_bonus(P1) == 0


def test_ger04_player1_turu_bitirince_sira_player2ye_gecer(game):
    ok, _ = game.process_action(P1, {"action": "END_TURN"})
    assert ok is True
    assert game.state.current_player == P2
    assert game.state.turn == 1
    assert game.state.phase == "DRAFT"
    assert game.state.unplaced_troops[P2] == 19  # ilk turda ek takviye yok


def test_ger04_tur_player2den_player1e_donunce_artar_ve_takviye_gelir(game):
    game.state.current_player = P2
    game.state.unplaced_troops[P1] = 0
    game.process_action(P2, {"action": "END_TURN"})
    assert game.state.current_player == P1
    assert game.state.turn == 2
    assert game.state.unplaced_troops[P1] >= 3


# --- GER-05: Kuvvet taşıma (FORTIFY) ve oyun sonu ---

def fortify_hazirla(game, bolgeler):
    """bolgeler: {bolge: asker}, hepsi player1'in; geri kalan player2'nin."""
    hepsini_ata(game, P2)
    for r, asker in bolgeler.items():
        game.state.update_region(r, P1, asker)
    game.state.current_player = P1
    game.state.phase = "FORTIFY"


def test_ger05_kesintisiz_yol_varsa_asker_tasinir_ve_tur_biter(game):
    fortify_hazirla(game, {"alaska": 5, "alberta": 1, "ontario": 1})
    ok, _ = game.process_action(P1, {"action": "FORTIFY", "from": "alaska", "to": "ontario", "amount": 3})
    assert ok is True
    assert game.state.regions["alaska"]["troops"] == 2
    assert game.state.regions["ontario"]["troops"] == 4
    assert game.state.current_player == P2


def test_ger05_arada_dusman_varsa_tasima_reddedilir(game):
    fortify_hazirla(game, {"alaska": 5, "japan": 1})
    ok, _ = game.process_action(P1, {"action": "FORTIFY", "from": "alaska", "to": "japan", "amount": 2})
    assert ok is False
    assert game.state.regions["alaska"]["troops"] == 5


def test_ger05_kaynak_bolgede_en_az_1_asker_kalmali(game):
    fortify_hazirla(game, {"alaska": 5, "alberta": 1})
    ok, _ = game.process_action(P1, {"action": "FORTIFY", "from": "alaska", "to": "alberta", "amount": 5})
    assert ok is False


def test_ger05_tum_bolgeler_ele_gecirilince_oyun_biter(game, monkeypatch):
    hepsini_ata(game, P1)
    game.state.update_region("mongolia", P1, 4)
    game.state.update_region("japan", P2, 1)
    game.state.current_player = P1
    game.state.phase = "ATTACK"
    zarlari_sabitle(monkeypatch, [6, 6, 6, 1])
    _, olay = saldir(game, "mongolia", "japan")
    assert olay["status"] == "GAME_OVER"
    assert olay["winner"] == P1
    assert game.state.phase == "GAME_OVER"


# --- Sunucu doğrulaması: istemciye güvenme (testle bulunan ve düzeltilen hatalar) ---

def test_ger02_kendi_bolgene_saldirilamaz(game):
    hepsini_ata(game, P1)
    game.state.update_region("alaska", P1, 4)
    game.state.current_player = P1
    game.state.phase = "ATTACK"
    ok, _ = saldir(game, "alaska", "alberta")
    assert ok is False


def test_ger02_rakibin_bolgesinden_saldirilamaz(game):
    saldiri_hazirla(game, "alaska", "alberta", 4, 1)
    game.state.update_region("alaska", P2, 4)  # kaynak bölge rakibin
    ok, _ = saldir(game, "alaska", "alberta")
    assert ok is False


@pytest.mark.parametrize("miktar", [-3, 0])
def test_ger03_gecersiz_takviye_miktari_reddedilir(game, miktar):
    bolge = kendi_bolgem(game)
    ok, _ = game.process_action(P1, {"action": "DRAFT", "region": bolge, "amount": miktar})
    assert ok is False
    assert game.state.unplaced_troops[P1] == 19  # yedek asker değişmemeli
    assert game.state.regions[bolge]["troops"] == 1