import socket
import pickle
import logging

from server.config import setup_logging
from threading import Thread

from shared.constants import MessageTypes
from server.game_logic import RiskGameLogic

setup_logging()


class GameRoom:
    def __init__(self, p1_data, p2_data):
        self.p1 = p1_data
        self.p2 = p2_data
        self.clients = [p1_data, p2_data]

        self.game_logic = RiskGameLogic()


class RiskServer:
    def __init__(self):
        self.waiting_players = []
        self.active_rooms = {}
        self.server_socket = None

        server_ip, server_port = ("", 5001)
        th = Thread(target=self.start_server, args=(server_ip, server_port))
        th.start()

    def start_server(self, server_ip, server_port):
        logging.info("Sunucu başlatılıyor...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((server_ip, server_port))
        self.server_socket.listen()
        logging.info(f"Risk Sunucusu {server_port} portunda çoklu odalar için hazır.")
        self.wait_connections()

    def wait_connections(self):
        logging.info("Oyuncuların bağlanması bekleniyor...")

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()

                try:
                    raw_identity = client_socket.recv(1024)
                    if not raw_identity: continue

                    identity = pickle.loads(raw_identity)

                    player_data = {
                        "socket": client_socket,
                        "name": identity["name"],
                        "char": identity["char"],
                        "thread_started": False,
                    }

                    self.waiting_players.append(player_data)
                    logging.info(
                        f"[{player_data['name']}] lobiye katıldı. Bekleyen oyuncu: {len(self.waiting_players)}")

                    self.match_players_from_lobby()

                except Exception as e:
                    logging.error(f"Kayıt hatası: {e}")
                    continue
            except OSError:
                break

    def match_players_from_lobby(self):
        while len(self.waiting_players) >= 2:
            p1 = self.waiting_players.pop(0)
            p2 = self.waiting_players.pop(0)

            p1["id"] = "player1"
            p2["id"] = "player2"

            room = GameRoom(p1, p2)

            self.active_rooms[p1["socket"]] = room
            self.active_rooms[p2["socket"]] = room

            logging.info(f"EŞLEŞME: {p1['name']} ve {p2['name']} yeni odaya alındı.")

            if not p1["thread_started"]:
                p1["thread_started"] = True
                Thread(target=self.message_listen_thread, args=(p1["socket"],), daemon=True).start()

            if not p2["thread_started"]:
                p2["thread_started"] = True
                Thread(target=self.message_listen_thread, args=(p2["socket"],), daemon=True).start()

            self.start_match(room)

    def message_listen_thread(self, client_socket):
        logging.info("Yeni bir dinleme kanalı (Thread) açıldı...")
        while True:
            try:
                message = client_socket.recv(4096)
                if not message:
                    break

                decoded_message = pickle.loads(message)

                room = self.active_rooms.get(client_socket)

                if not room:
                    if isinstance(decoded_message, dict) and decoded_message.get("type") == MessageTypes.DISCONNECT:
                        logging.info("Oyuncu lobideyken çıkış yaptı.")
                        self.close_connection(client_socket)
                        return
                    continue  # Lobideyken gelen oyun hamlelerini yoksay

                player_id = room.p1["id"] if room.p1["socket"] == client_socket else room.p2["id"]

                if isinstance(decoded_message, dict) and decoded_message.get("type") == MessageTypes.DISCONNECT:
                    logging.info(
                        f"[{room.p1['name']} vs {room.p2['name']}] Odası - Oyuncu {player_id} güvenli çıkış yaptı.")
                    self.close_connection(client_socket)
                    return

                logging.info(f"[{room.p1['name']} vs {room.p2['name']}] Odası - {player_id} hamlesi: {decoded_message}")

                success, msg = room.game_logic.process_action(player_id, decoded_message)

                if success:
                    if isinstance(msg, dict):
                        self.broadcast_to_room(room, msg)
                    self.broadcast_to_room(room, room.game_logic.state)
                else:
                    error_msg = {"type": "ERROR", "message": msg}
                    client_socket.sendall(pickle.dumps(error_msg))

            except OSError as e:
                if e.errno == 9:
                    logging.debug(f"Oyuncu {player_id} için soket kapatıldı. Thread sonlandırılıyor.")
                else:
                    logging.error(f"Soket Hatası (OS): {e}")
                return

            except (ConnectionResetError, EOFError):
                logging.error(f"Oyuncu {player_id} bağlantısı koptu.")
                self.close_connection(client_socket)
                return

            except Exception as e:
                logging.error(f"Beklenmeyen Hata: {e}")
                self.close_connection(client_socket)
                return

    def start_match(self, room):
        p1, p2 = room.p1, room.p2

        info_p1 = {
            "type": MessageTypes.CONNECTION_INFO,
            "assigned_id": "player1",
            "opponent_name": p2['name'],
            "opponent_char": p2['char']
        }
        p1["socket"].sendall(pickle.dumps(info_p1))

        info_p2 = {
            "type": MessageTypes.CONNECTION_INFO,
            "assigned_id": "player2",
            "opponent_name": p1['name'],
            "opponent_char": p1['char']
        }
        p2["socket"].sendall(pickle.dumps(info_p2))

        start_msg = {"type": MessageTypes.GAME_START}
        p1["socket"].sendall(pickle.dumps(start_msg))
        p2["socket"].sendall(pickle.dumps(start_msg))

        initial_state_bytes = pickle.dumps(room.game_logic.state)
        p1["socket"].sendall(initial_state_bytes)
        p2["socket"].sendall(initial_state_bytes)

    def broadcast_to_room(self, room, data_object):
        try:
            data_bytes = pickle.dumps(data_object)
            for client in room.clients:
                try:
                    client["socket"].sendall(data_bytes)
                except Exception as e:
                    logging.error(f"Oda içi broadcast hatası: {e}")
        except Exception as e:
            logging.error(f"Pickle paketleme hatası: {e}")

    def close_connection(self, client_socket):
        # 1. ihtimal: Oyuncu lobideyken (henüz eşleşmeden) çıktıysa
        for p in self.waiting_players:
            if p["socket"] == client_socket:
                self.waiting_players.remove(p)
                client_socket.close()
                logging.info(f"{p['name']} eşleşmeden lobiden ayrıldı.")
                return

        # 2. ihtimal: Oyuncu aktif bir maçtayken çıktıysa
        room = self.active_rooms.get(client_socket)
        if room:
            leaving_player = room.p1 if room.p1["socket"] == client_socket else room.p2
            remaining_player = room.p2 if room.p1["socket"] == client_socket else room.p1

            logging.info(f"{leaving_player['name']} oyundan düştü/ayrıldı. Oda kapatılıyor.")

            try:
                leaving_player["socket"].close()
            except:
                pass

            try:
                info = {"type": MessageTypes.OPPONENT_LEFT}
                remaining_player["socket"].sendall(pickle.dumps(info))

                remaining_player["socket"].close()
            except:
                pass

            if room.p1["socket"] in self.active_rooms: del self.active_rooms[room.p1["socket"]]
            if room.p2["socket"] in self.active_rooms: del self.active_rooms[room.p2["socket"]]

    def stop(self):
        logging.info("Sunucu tamamen kapatılıyor...")

        # Tüm odalardaki oyuncuları at
        for sock in list(self.active_rooms.keys()):
            try:
                sock.close()
            except:
                pass
        self.active_rooms.clear()

        # Lobidekileri at
        for p in self.waiting_players:
            try:
                p["socket"].close()
            except:
                pass
        self.waiting_players.clear()

        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None