
from client.network.tcp_client import TCPClient
class Player:
    def __init__(self, name: str, player_id: str= None, client_obj=None):
        self.name = name
        self.id = player_id
        self.client = client_obj
        self.character_image = None
        self.armies = 0
        self.regions = []
        self.is_turn = False

    def send_action(self, action_data: dict):
        if self.client:
            # Oyuncu, içindeki client nesnesini kullanarak veriyi paketler ve gönderir
            self.client.send_message(action_data)
