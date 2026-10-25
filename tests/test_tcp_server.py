import pickle
import socket
import time

import pytest

from server.tcp_server import RiskServer
from shared.constants import MessageTypes, REGION_NEIGHBORS

HOST = "127.0.0.1"
ZAMAN_ASIMI = 5


def bekle(kosul, sure=ZAMAN_ASIMI):
    """Koşul doğru olana kadar kısa aralıklarla dener (sabit sleep yerine)."""
    bitis = time.time() + sure
    while time.time() < bitis:
        if kosul():
            return True
        time.sleep(0.02)
    return False


class SahteIstemci:
    """Gerçek bir oyuncu gibi sunucuya TCP ile bağlanan test istemcisi."""

    def __init__(self, port, isim, karakter="char1"):
        self.sock = self._baglan(port)
        # makefile + pickle.load: arka arkaya gelen birden fazla nesneyi tek tek okur
        self.dosya = self.sock.makefile("rb")
        self.sock.sendall(pickle.dumps({"name": isim, "char": karakter}))

    @staticmethod
    def _baglan(port):
        bitis = time.time() + ZAMAN_ASIMI
        while True:
            try:
                return socket.create_connection((HOST, port), timeout=ZAMAN_ASIMI)
            except ConnectionRefusedError:  # sunucu henüz listen() çağırmamış olabilir
                if time.time() > bitis:
                    raise
                time.sleep(0.02)

    def al(self):
        return pickle.load(self.dosya)

    def gonder(self, veri):
        self.sock.sendall(pickle.dumps(veri))

    def kapat(self):
        for kaynak in (self.dosya, self.sock):
            try:
                kaynak.close()
            except OSError:
                pass


@pytest.fixture
def sunucu():
    server = RiskServer(HOST, 0)  # port 0: işletim sistemi boş bir port seçer
    assert bekle(lambda: server.server_socket is not None
                 and server.server_socket.getsockname()[1] != 0), "Sunucu açılmadı"
    port = server.server_socket.getsockname()[1]
    yield server, port
    try:  # accept() bekleyen thread'i uyandırmak için (Linux'ta close() yetmez)
        server.server_socket.shutdown(socket.SHUT_RDWR)
    except (OSError, AttributeError):
        pass
    server.stop()


@pytest.fixture
def istemciler():
    liste = []
    yield liste
    for i in liste:
        i.kapat()


def baglan(istemciler, port, isim):
    istemci = SahteIstemci(port, isim)
    istemciler.append(istemci)
    return istemci


@pytest.fixture
def mac(sunucu, istemciler):
    """İki oyuncu bağlanır, ilk mesajlar okunur; (server, a, b, ilk_durum) döner."""
    server, port = sunucu
    a = baglan(istemciler, port, "Ayse")
    assert bekle(lambda: len(server.waiting_players) == 1)
    b = baglan(istemciler, port, "Bora")
    for oyuncu in (a, b):
        oyuncu.al()  # CONN_INFO
        oyuncu.al()  # GAME_START
    durum_a = a.al()
    b.al()
    return server, a, b, durum_a


# --- GER-06: Lobi ve eşleştirme ---

def test_ger06_tek_oyuncu_lobide_bekler(sunucu, istemciler):
    server, port = sunucu
    baglan(istemciler, port, "Ayse")
    assert bekle(lambda: len(server.waiting_players) == 1)
    assert server.active_rooms == {}


def test_ger06_iki_oyuncu_eslesir_ve_roller_dagitilir(sunucu, istemciler):
    server, port = sunucu
    a = baglan(istemciler, port, "Ayse")
    assert bekle(lambda: len(server.waiting_players) == 1)
    b = baglan(istemciler, port, "Bora")

    bilgi_a, bilgi_b = a.al(), b.al()
    assert bilgi_a["type"] == MessageTypes.CONNECTION_INFO
    assert bilgi_a["assigned_id"] == "player1"
    assert bilgi_a["opponent_name"] == "Bora"
    assert bilgi_b["assigned_id"] == "player2"
    assert bilgi_b["opponent_name"] == "Ayse"
    assert len(server.active_rooms) == 2  # oda iki sokete de bağlı
    assert server.waiting_players == []


def test_ger06_mac_baslayinca_oyun_baslangic_durumu_gelir(mac):
    _, _, _, durum = mac
    assert durum.current_player == "player1"
    assert durum.phase == "DRAFT"
    assert len(durum.regions) == 42


# --- GER-07: Hamle işleme ---

def test_ger07_gecerli_hamle_iki_oyuncuya_yayinlanir(mac):
    _, a, b, durum = mac
    bolge = next(r for r, d in durum.regions.items() if d["owner"] == "player1")
    a.gonder({"action": "DRAFT", "region": bolge, "amount": 1})

    for oyuncu in (a, b):
        yeni = oyuncu.al()
        assert yeni.regions[bolge]["troops"] == 2
        assert yeni.unplaced_troops["player1"] == 18


def test_ger07_sirasi_olmayan_oyuncu_sadece_kendisi_hata_alir(mac):
    _, a, b, durum = mac
    bolge = next(r for r, d in durum.regions.items() if d["owner"] == "player2")
    b.gonder({"action": "DRAFT", "region": bolge, "amount": 1})

    assert b.al() == {"type": "ERROR", "message": "Sıra sizde değil!"}
    a.sock.settimeout(0.3)
    with pytest.raises(socket.timeout):  # player1'e hiçbir şey gönderilmemeli
        a.al()


# --- GER-08: Bağlantı kopması ---

def test_ger08_guvenli_cikista_rakip_bilgilendirilir(mac):
    server, a, b, _ = mac
    a.gonder({"type": MessageTypes.DISCONNECT})

    assert b.al() == {"type": MessageTypes.OPPONENT_LEFT}
    assert bekle(lambda: server.active_rooms == {})


def test_ger08_ani_baglanti_kapaninca_oda_temizlenir_ve_rakibe_haber_gider(mac):
    server, a, b, _ = mac
    a.kapat()  # DISCONNECT mesajı göndermeden kapat (uygulama çökmesi gibi)

    assert b.al() == {"type": MessageTypes.OPPONENT_LEFT}
    assert bekle(lambda: server.active_rooms == {})


# --- GER-09: Saldırı sonucu ve oyun bitişi ağ üzerinden ---

def oda_durumunu_hazirla(server, bolgeler, faz="ATTACK"):
    """Sunucudaki odanın oyun durumunu kurar: {bolge: (sahip, asker)}, geri kalan player2'nin."""
    oda = next(iter(server.active_rooms.values()))
    durum = oda.game_logic.state
    for r in REGION_NEIGHBORS:
        durum.update_region(r, "player2", 1)
    for r, (sahip, asker) in bolgeler.items():
        durum.update_region(r, sahip, asker)
    durum.current_player = "player1"
    durum.phase = faz


def zarlari_sabitle(monkeypatch, degerler):
    it = iter(degerler)
    monkeypatch.setattr("server.game_logic.random.randint", lambda a, b: next(it))


def test_ger09_saldiri_sonucu_ve_yeni_durum_iki_oyuncuya_yayinlanir(mac, monkeypatch):
    server, a, b, _ = mac
    oda_durumunu_hazirla(server, {"alaska": ("player1", 4), "kamchatka": ("player2", 2)})
    zarlari_sabitle(monkeypatch, [6, 1, 1, 3, 3])  # saldıran 6,1,1 - savunan 3,3: ikisi de 1 kayıp
    a.gonder({"action": "ATTACK", "from": "alaska", "to": "kamchatka"})

    for oyuncu in (a, b):
        sonuc = oyuncu.al()
        assert sonuc["type"] == "BATTLE_RESULT"
        assert sonuc["status"] == "ONGOING"
        assert (sonuc["att_loss"], sonuc["def_loss"]) == (1, 1)
        yeni = oyuncu.al()  # sonuçtan sonra güncel oyun durumu gelir
        assert yeni.regions["alaska"]["troops"] == 3
        assert yeni.regions["kamchatka"]["troops"] == 1


def test_ger09_tum_bolgeler_alininca_oyun_biter_ve_kazanan_duyurulur(mac, monkeypatch):
    server, a, b, _ = mac
    oda_durumunu_hazirla(server, {r: ("player1", 1) for r in REGION_NEIGHBORS}
                         | {"mongolia": ("player1", 4), "japan": ("player2", 1)})
    zarlari_sabitle(monkeypatch, [6, 6, 6, 1])
    a.gonder({"action": "ATTACK", "from": "mongolia", "to": "japan"})

    for oyuncu in (a, b):
        sonuc = oyuncu.al()
        assert sonuc["status"] == "GAME_OVER"
        assert oyuncu.al() == {"type": "GAME_OVER", "winner": "player1"}
        son_durum = oyuncu.al()
        assert son_durum.phase == "GAME_OVER"


# --- GER-10: Lobi ---

@pytest.mark.xfail(strict=True, reason="BUG: lobide bekleyen oyuncu bağlantıyı kapatınca kuyruktan silinmiyor "
                                       "(dinleme thread'i sadece eşleşmeden sonra başlıyor), "
                                       "sonraki oyuncu hayalet oyuncuyla eşleşebilir")
def test_ger10_lobiden_ayrilan_oyuncu_kuyruktan_silinir(sunucu, istemciler):
    server, port = sunucu
    a = baglan(istemciler, port, "Ayse")
    assert bekle(lambda: len(server.waiting_players) == 1)
    a.kapat()
    assert bekle(lambda: server.waiting_players == [], sure=2)