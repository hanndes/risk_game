import socket
import pickle
import logging
import threading
from threading import Thread
from typing import Optional, Callable

from shared.constants import MessageTypes
from client.utils.config import setup_logging
from PyQt6.QtCore import pyqtSignal, QObject

setup_logging()

class NetworkSignals(QObject):
    state_updated = pyqtSignal(object)

class TCPClient:
    def __init__(self, player_name, player_char):

        self.player_name = player_name
        self.player_char = player_char
        self.listen_thread: Optional[Thread] = None
        self.client_socket: Optional[socket.socket] = None

        self.signals = NetworkSignals()

        server_ip, server_port = ("127.0.0.1", 5001)
        th = Thread(target=self.start_client, args=(server_ip, server_port))
        th.daemon = True
        th.start()

        self.lock = threading.Lock()

    def start_client(self, server_ip, server_port):
        logging.info("İstemci başlatılıyor...")
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))

            self.client_socket = client_socket
            logging.info(f"Sunucuya bağlanıldı: {server_ip}:{server_port}")

            signup_msg = {
                "type": MessageTypes.SIGN_UP,
                "name": self.player_name,
                "char": self.player_char
            }

            # pickle.dumps: Veriyi ağdan geçebilecek bytea çevirir
            self.client_socket.sendall(pickle.dumps(signup_msg))

            self.listen_thread = Thread(target=self.message_listen_thread)
            self.listen_thread.daemon = True
            self.listen_thread.start()

        except ConnectionRefusedError:
            logging.error("Sunucuya bağlanılamadı. Sunucunun çalıştığından emin olun.")

    def message_listen_thread(self):
        if not self.client_socket:
            return

        logging.info("Mesaj dinleme thread'i başlatıldı.")

        try:
            socket_file = self.client_socket.makefile('rb')

            while True:
                try:
                    # buffer = recv(4096) yerine doğrudan dosyadan yükler gibi alıyoruz
                    decoded_message = pickle.load(socket_file)
                    logging.info(f"Sunucudan nesne alındı: {decoded_message}")

                    self.signals.state_updated.emit(decoded_message)

                except EOFError:
                    # Sunucu bağlantıyı kapattığında (dosya sonuna gelindiğinde) burası çalışır
                    logging.warning("Sunucu bağlantısı kapandı (EOF).")
                    break
                except ConnectionResetError:
                    logging.error("Sunucu bağlantısı beklenmedik şekilde sıfırlandı.")
                    break
                except Exception as e:
                    logging.error(f"Gelen veri okunamadı: {e}")
                    break

        except Exception as e:
            logging.error(f"Soket dosya okuyucu hatası: {e}")

        self.close_connection()

    def send_message(self, data: dict):
        if not self.client_socket:
            logging.warning("Bağlantı yok, mesaj gönderilemedi.")
            return

        try:
            message = pickle.dumps(data)
            self.client_socket.sendall(message)
            logging.info(f"Mesaj gönderildi: {data}")

        except ConnectionError as e:
            logging.error(f"Mesaj gönderilemedi: {e}")
            self.close_connection()

    def send_disconnect_message(self):
        if self.client_socket:
            try:
                disconnect_msg = {"type": MessageTypes.DISCONNECT}
                self.send_message(disconnect_msg)
            except Exception as e:
                logging.error(f"Çıkış mesajı gönderilemedi: {e}")

    def close_connection(self):
        with self.lock:
            if self.client_socket is None:
                return

            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                self.client_socket.close()
                self.client_socket = None
                logging.info("Sunucu bağlantısı güvenli kapatıldı.")