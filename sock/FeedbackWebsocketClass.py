from websockets.sync.client import connect
from sock.socketClass import Websocket
from multiprocessing import Pipe


class FeedbackWebsocket(Websocket):

    def __init__(self, uri: str):
        super().__init__(uri)
        # self.websocket = connect(self.uri)

        self.receiver, self.sender = Pipe()
    
    @Websocket._connect_and_run
    def connect_and_forward(self):
        """
        Connects to the websocket and waits for messages to forward them
        """
        try:
            while 1:
                message = self.receiver.recv()
                self.websocket.send(message)

                if self.closed.is_set():
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            pass
        finally:
            print("FeedbackWebsocket>>> Closing...")

            self.closed.set()
    
    def connect_and_forward_windows(self):
        """ Same as FeedbackWebsocket.connect_and_forward() - workaround for Windows """
        self.connect_and_forward()

    def send(self, message: str) -> None:
        self.sender.send(message)
