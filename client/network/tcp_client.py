# client/network/tcp_client.py

import socket
import pickle
import logging
from threading import Thread
from typing import Optional, Callable

from shared.constants import MessageTypes
from client.utils.config import setup_logging

setup_logging()


class TCPClient:
    def __init__(self, player_name, player_char, on_message_received_callback):

        self.player_name = player_name
        self.player_char = player_char
        self.on_message_received_callback = on_message_received_callback
        self.listen_thread: Optional[Thread] = None
        self.client_socket: Optional[socket.socket] = None

        server_ip, server_port = ("127.0.0.1", 5001)
        th = Thread(target=self.start_client, args=(server_ip, server_port))
        th.daemon = True
        th.start()


    def start_client(self, server_ip, server_port):
        logging.info("[CLIENT] İstemci başlatılıyor...")
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))

            self.client_socket = client_socket
            logging.info(f"[CLIENT] Sunucuya bağlanıldı: {server_ip}:{server_port}")

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
            logging.error("[CLIENT] Sunucuya bağlanılamadı. Sunucunun çalıştığından emin olun.")

    def message_listen_thread(self):
        if not self.client_socket:
            return

        logging.info("[CLIENT] Mesaj dinleme thread'i başlatıldı.")

        while self.client_socket:
            try:
                message = self.client_socket.recv(1024)
                if not message:
                    logging.warning("[CLIENT] Sunucudan boş mesaj alındı, bağlantı kapanıyor.")
                    break

                decoded_message = pickle.loads(message)
                logging.info(f"[CLIENT] Sunucudan mesaj alındı: {decoded_message}")

                if self.on_message_received_callback:
                    self.on_message_received_callback(decoded_message)

            except ConnectionResetError:
                logging.error("[CLIENT] Sunucu bağlantısı beklenmedik şekilde kapandı.")
                break
            except EOFError:
                logging.error("[CLIENT] Gelen veri işlenemedi veya eksik (EOFError).")
                break

        self.close_connection()

    def send_message(self, data: dict):
        if not self.client_socket:
            logging.warning("[CLIENT] Bağlantı yok, mesaj gönderilemedi.")
            return

        try:
            message = pickle.dumps(data)
            self.client_socket.sendall(message)
            logging.info(f"[CLIENT] Mesaj gönderildi: {data}")

        except ConnectionError as e:
            logging.error(f"[CLIENT] Mesaj gönderilemedi: {e}")
            self.close_connection()

    def close_connection(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            logging.info("[CLIENT] Sunucu bağlantısı kapatıldı.")