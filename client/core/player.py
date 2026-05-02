
from network.tcp_client import TCPClient
class Player:
    def __init__(self, name: str, client: TCPClient):
        self.name = name
        self.armies = 0
        self.regions = []
        self.client = client
