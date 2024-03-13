from websockets.sync.client import connect
from sock.socketClass import Websocket


class FeedbackWebsocket(Websocket):

    def __init__(self, uri: str):
        super().__init__(uri)
        self.websocket = connect(self.uri)

    def send(self, message: str) -> None:
        self.websocket.send(message)
