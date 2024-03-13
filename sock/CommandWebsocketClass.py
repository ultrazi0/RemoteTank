import json

from multiprocessing import Pipe
from sock.socketClass import Websocket


class CommandWebsocket(Websocket):
    def __init__(self, uri: str):
        super().__init__(uri)
        self.receiver, self.sender = Pipe()

    @Websocket._connect_and_run
    def receive_commands(self):
        """
        Receives commands from websocket and sends them via Pipe
        WORKS ONLY ON UNIX-BASES SYSTEMS, FOR WINDOWS USE: CommandWebsocket.receive_commands_windows()
        """
        try:
            while 1:
                try:
                    json_commands = self.websocket.recv(15)

                    try:
                        message = json.loads(json_commands)
                        if type(message) == dict:
                            # If only one command, change type to list
                            message = [message]
                        self.sender.send(message)
                    except ValueError:
                        print("CommandWebsocket>>> Received non-JSON message:", json_commands)

                    if self.closed.is_set():
                        raise KeyboardInterrupt
                except TimeoutError:
                    pass
        except KeyboardInterrupt:
            pass
        finally:
            print("CommandWebsocket>>> Closing...")

            self.closed.set()

    def receive_commands_windows(self):
        """ Same as CommandWebsocket.receive_commands() - workaround for Windows """
        self.receive_commands()
