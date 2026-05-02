
from client.network.tcp_client import TCPClient
class Player:
    def __init__(self, name: str, client_obj=None):
        self.name = name
        self.client = client_obj
        self.character_image = "default.png"
        self.armies = 0
        self.regions = []
        self.is_turn = False

    def send_action(self, action_data: dict):
        if self.client:
            # Oyuncu, içindeki client nesnesini kullanarak veriyi paketler ve gönderir[cite: 6, 8].
            self.client.send_message(action_data)
