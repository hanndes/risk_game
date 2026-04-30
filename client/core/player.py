class Player:
    def __init__(self, name):
        self.name = name
        self.id = None
        self.character_image = None

    def __str__(self):
        return f"Oyuncu: {self.name} | Karakter: {self.character_image}"