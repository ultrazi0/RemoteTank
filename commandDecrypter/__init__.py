from commandDecrypter.DecrypterClass import *


if __name__ == "__main__":
    from sock import ImageWebsocket
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

    r = dec.decrypt_and_execute(message)

    print(r)
