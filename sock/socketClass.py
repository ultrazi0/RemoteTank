from os import getpid
from multiprocessing import Event
from websockets.sync.client import connect


class Websocket:
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.closed = Event()

    @staticmethod
    def _connect_and_run(func):
        """
        This function is designed as a decorator. Use ONLY in child classes
        This decorator connects to a websocket and executes given function.
        """
        def inside(self, *args, **kwargs):

            with connect(self.uri) as websocket:
                print(f'Websocket>>> Connected to websocket at "{self.uri}" in process {getpid()}')
                self.websocket = websocket

                try:
                    func(self, *args, **kwargs)
                except KeyboardInterrupt:
                    pass
                finally:
                    self.closed.set()
                    print(f'Websocket>>> Closing websocket at "{self.uri}" in process {getpid()}...')

        return inside
