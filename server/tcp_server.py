import socket
import pickle
import logging
from config import setup_logging
from threading import Thread
from shared.constants import MessageTypes

setup_logging()

class RiskServer:
    def __init__(self):
        self.clients = []
        self.server_socket = None

        server_ip, server_port = ("", 5001)
        th = Thread(target=self.start_server, args=(server_ip, server_port))
        th.start()

    def start_server(self, server_ip, server_port):
        logging.info("[SERVER] Sunucu başlatılıyor...")
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

            try:
                raw_identity = client_socket.recv(1024)
                identity = pickle.loads(raw_identity) # {type: "SIGN_UP", name: "Ceyda", char: "..."}

                player_data = {
                    "socket": client_socket,
                    "name": identity["name"],
                    "char": identity["char"]
                }
                self.clients.append(player_data)
                player_id = len(self.clients)
                logging.info(f"Oyuncu {player_id} ({player_data['name']}) bağlandı.")

                listen_thread = Thread(target=self.message_listen_thread, args=(client_socket, player_id))
                listen_thread.daemon = True
                listen_thread.start()

            except Exception as e:
                logging.error(f"Kayıt hatası: {e}")
                continue

            if len(self.clients) == 2:
                self.match_player()

    def message_listen_thread(self, client_socket, player_id):
        logging.info(f"Oyuncu {player_id} dinleniyor...")
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                # alınan ham byte yığınını pickle ile python nesnesine çevirir
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

    def match_player(self):
        if len(self.clients) < 2:
            return

        p1, p2 = self.clients[0], self.clients[1]

        for sender, opponent in [(p1, p2), (p2, p1)]:
            info = {
                "type": MessageTypes.CONNECTION_INFO,
                "opponent_name": opponent['name'],
                "opponent_char": opponent['char']
            }
            sender["socket"].sendall(pickle.dumps(info))

        start_msg = {"type": MessageTypes.GAME_START}
        p1["socket"].sendall(pickle.dumps(start_msg))
        p2["socket"].sendall(pickle.dumps(start_msg))

        logging.info("Oyuncular eşleştirildi ve oyun başlatılıyor.")

    def broadcast_message(self, message, sender_socket):
        for client in self.clients:
            if client["socket"] != sender_socket:
                try:
                    client["socket"].sendall(message)
                except:
                    self.close_connection(client)

    def close_connection(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
            client_socket.close()

        if len(self.clients) == 0 and self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            logging.info("Tüm oyuncular ayrıldı, sunucu kapatıldı.")

