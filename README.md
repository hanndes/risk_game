# Risk Oyunu — Çok Oyunculu Ağ Tabanlı Masaüstü Uygulaması

Python ve PyQt6 ile geliştirilmiş, TCP soket altyapısı üzerine kurulu 2 kişilik Risk masa oyunu.

---

## Özellikler

- 2 oyunculu gerçek zamanlı çok oyunculu mod (TCP/IP)
- Klasik Risk haritası (42 bölge, 6 kıta)
- Tam oyun döngüsü: **Takviye → Saldırı → Kuvvet Taşıma**
- Zar animasyonları ve savaş sonucu ekranı
- Kıta bonusu hesaplama sistemi
- Lobi ve eşleşme bekleme ekranı
- Oyuncu ayrıldığında otomatik bildirim

---

## Gereksinimler

- Python 3.9+
- PyQt6

```bash
pip install -r requirements.txt
```

---

## Çalıştırma

### 1. Sunucuyu Başlat

```bash
python server/server_main.py
```

Sunucu `5001` portunda dinlemeye başlar ve 2 oyuncu bağlanınca otomatik eşleştirir.

### 2. İstemciyi Başlat (her oyuncu için ayrı terminal)

```bash
cd client
python client_main.py
```

Giriş ekranından bir kullanıcı adı gir ve sunucuya bağlan. İki oyuncu da bağlandığında oyun otomatik başlar.

---

## Proje Yapısı

```
risk_game/
├── server/
│   ├── server_main.py      # Sunucu giriş noktası
│   ├── tcp_server.py       # TCP bağlantı yönetimi ve lobi sistemi
│   ├── game_logic.py       # Oyun kuralları ve faz yönetimi
│   └── config.py           # Loglama yapılandırması
│
├── client/
│   ├── client_main.py      # İstemci giriş noktası
│   ├── client_controller.py# Pencere yönetimi ve ağ mesaj yönlendirmesi
│   ├── core/
│   │   └── player.py       # Oyuncu modeli
│   ├── network/
│   │   └── tcp_client.py   # TCP bağlantı istemcisi
│   ├── views/
│   │   ├── login_view.py       # Giriş ekranı
│   │   ├── waiting_room_view.py# Eşleşme bekleme ekranı
│   │   ├── game_view.py        # Ana oyun ekranı
│   │   └── end_view.py         # Oyun sonu ekranı
│   ├── utils/
│   │   ├── map_parser.py   # SVG harita ayrıştırıcı
│   │   └── config.py       # İstemci yapılandırması
│   └── assets/
│       └── images/         # Harita, zar ve arka plan görselleri
│
└── shared/
    ├── game_state.py       # Paylaşılan oyun durumu modeli
    └── constants.py        # Bölge komşulukları, kıta tanımları, mesaj tipleri
```

---

## Oyun Kuralları

### Oyun Başlangıcı
42 bölge iki oyuncu arasında rastgele eşit şekilde dağıtılır (21'er bölge). Her oyuncunun yerleştirmesi için 19 yedek askeri vardır.

### Tur Fazları

| Faz | Açıklama |
|-----|----------|
| **Takviye (DRAFT)** | Yedek askerlerini kendi bölgelerine yerleştir. |
| **Saldırı (ATTACK)** | Komşu düşman bölgelere zar atarak saldır. |
| **Kuvvet Taşıma (FORTIFY)** | Kendi bölgelerin arasında asker kaydır, tur biter. |

### Takviye Hesaplama
Her turun başında oyuncuya şu kadar asker eklenir:
- `max(3, sahip olunan bölge sayısı / 3)` — bölge bonusu
- Kıtanın tamamına sahip olunursa ek kıta bonusu

### Kıta Bonusları

| Kıta | Bonus |
|------|-------|
| Kuzey Amerika | +5 |
| Güney Amerika | +2 |
| Avrupa | +5 |
| Afrika | +3 |
| Asya | +7 |
| Avustralya | +2 |

### Saldırı Mekanizması
- Saldıran en fazla 3, savunan en fazla 2 zar atar.
- Zarlar yüksekten düşüğe sıralanır ve birer birer karşılaştırılır; beraberlikte savunan kazanır.
- Savunanın son askeri de düşerse bölge el değiştirir; saldırandan zar sayısı kadar asker yeni bölgeye geçer.

### Kazanma Koşulu
Rakibin tüm 42 bölgesini ele geçiren oyuncu oyunu kazanır.

---

## Teknik Notlar

- Sunucu ve istemci arasındaki iletişim `pickle` ile serileştirilmiş Python nesneleridir.
- Her oda bağımsız bir `GameRoom` örneğidir; sunucu aynı anda birden fazla oyun yürütebilir.
- Kuvvet taşıma fazında yol doğrulaması BFS (Breadth-First Search) algoritmasıyla yapılır; yalnızca oyuncunun kendi bölgeleri üzerinden geçen kesintisiz yollar geçerlidir.
