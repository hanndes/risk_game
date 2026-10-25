from collections import deque

from shared.constants import CONTINENTS, REGION_NEIGHBORS
from shared.game_state import GameState


# --- Harita verisi (constants.py) ---

def test_harita_42_bolgeden_olusur():
    assert len(REGION_NEIGHBORS) == 42


def test_her_bolge_tam_olarak_bir_kitadadir():
    kita_bolgeleri = [r for veri in CONTINENTS.values() for r in veri["regions"]]
    assert len(kita_bolgeleri) == len(set(kita_bolgeleri)), "Bir bölge birden fazla kıtada"
    assert set(kita_bolgeleri) == set(REGION_NEIGHBORS), "Kıtalarla harita bölgeleri uyuşmuyor"


def test_komsular_haritada_tanimli_olmali():
    tanimsiz = [(r, n) for r, komsular in REGION_NEIGHBORS.items()
                for n in komsular if n not in REGION_NEIGHBORS]
    assert tanimsiz == []


def test_bolge_kendisinin_komsusu_olamaz():
    assert [r for r, komsular in REGION_NEIGHBORS.items() if r in komsular] == []


def test_komsuluk_karsilikli_olmali():
    tek_yonlu = [(r, n) for r, komsular in REGION_NEIGHBORS.items()
                 for n in komsular if r not in REGION_NEIGHBORS.get(n, [])]
    assert tek_yonlu == [], f"Karşılıklı olmayan komşuluklar: {tek_yonlu}"


def test_harita_tek_parca_baglantili():
    baslangic = next(iter(REGION_NEIGHBORS))
    gorulen, kuyruk = {baslangic}, deque([baslangic])
    while kuyruk:
        for komsu in REGION_NEIGHBORS[kuyruk.popleft()]:
            if komsu not in gorulen:
                gorulen.add(komsu)
                kuyruk.append(komsu)
    assert gorulen == set(REGION_NEIGHBORS)


# --- GameState (game_state.py) ---

def test_baslangic_durumu():
    state = GameState()
    assert state.turn == 1
    assert state.phase == "DRAFT"
    assert state.unplaced_troops == {"player1": 19, "player2": 19}


def test_update_region_bolgeyi_kaydeder():
    state = GameState()
    state.update_region("alaska", "player1", 5)
    assert state.regions["alaska"] == {"owner": "player1", "troops": 5}