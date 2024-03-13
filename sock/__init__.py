from sock.socketClass import *
from sock.ImageWebsocketClass import *
from sock.CommandWebsocketClass import *
from sock.FeedbackWebsocketClass import *


if __name__ == "__main__":
    from multiprocessing import Process
    from commandDecrypter.DecrypterClass import CommandDecrypter

    ws = CommandWebsocket("ws://localhost:8080/command/topic")

    read = Process(target=ws.receive_commands_windows, args=())

    def my_print(str1, str2):
        print(str1, str2)

    commands = {
        "PRINT": my_print
    }

    message = {
        "command": "PRINT",
        "values": {
            "str1": "hello",
            "str2": "world"
        }
    }

    dec = CommandDecrypter(commands)

    try:
        read.start()

        message = ws.receiver.recv()

        print("Received:", message)

        print(dec.decrypt_and_execute(message))

        read.join()
    except KeyboardInterrupt:
        pass
    finally:
        ws.closed.set()
        print("THE END")
