class GameMessage:
    def __init__(self, msg_type, data=None):
        self.msg_type = msg_type
        self.data = data or {}

    def to_dict(self):
        return {"type": self.msg_type, "payload": self.data}