import socket
import pickle
import logging
from config import setup_logging
from threading import Thread

setup_logging()

class RiskServer:
    def __init__(self):
        self.clients = []
        self.server_socket = None

        server_ip, server_port = ("", 5001)
        th = Thread(target=self.start_server, args=(server_ip, server_port))
        th.start()

    def start_server(self, server_ip, server_port):
        print("[SERVER] Sunucu başlatılıyor...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((server_ip, server_port))
        self.server_socket.listen()

        logging.info(f"Risk Sunucusu {server_port} portunda hazır.")

        self.wait_connections()

    def wait_connections(self):
        logging.info("Oyuncuların bağlanması bekleniyor...")

        # 2 kişi bağlanana kadar bekleme döngüsü içerisinde
        while len(self.clients) < 2:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)

            player_id = len(self.clients)
            logging.info(f"Oyuncu {player_id} bağlandı: {client_address}")

            listen_thread = Thread(target=self.message_listen_thread, args=(client_socket, player_id))
            listen_thread.start()

        logging.info("İki oyuncu da hazır. Oyun başlıyor!")

    def message_listen_thread(self, client_socket, player_id):
        logging.info(f"Oyuncu {player_id} dinleniyor...")
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                # alınan ham byte yığınını pickle ile python nesnesine çevirir.
                decoded_message = pickle.loads(message)
                logging.info(f"Oyuncu {player_id} hamlesi alındı: {decoded_message}")

                self.broadcast_message(message, sender_socket=client_socket)
            except ConnectionResetError:
                logging.error(f"Oyuncu {player_id} bağlantısı koptu.")
                self.close_connection(client_socket)
                return
            except EOFError:
                logging.error(f"Oyuncu {player_id} verisi işlenemedi veya eksik.")
                self.close_connection(client_socket)
                return

    def broadcast_message(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.sendall(message)
                except
                    self.close_connection(client)

    def close_connection(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
            client_socket.close()

        if len(self.clients) == 0 and self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            logging.info("Tüm oyuncular ayrıldı, sunucu kapatıldı.")

