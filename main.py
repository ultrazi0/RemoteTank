
if __name__ == "__main__":
    from multiprocessing import Process
    from commandDecrypter import CommandDecrypter
    from camera import Camera
    from sock import ImageWebsocket, CommandWebsocket


    def my_move(speed, turn):
        print(f"Main>>> I have been moved with the speed {speed} in direction {turn}")

    def my_turret(tilt, turn):
        print(f"Main>>> I have been tilted by {tilt} and turned by {turn}")

    def my_shoot():
        print(">>> Yes, Sir! Shooting!")


    commands = {
        "MOVE": my_move,
        "TURRET": my_turret,
        "SHOOT": my_shoot
    }

    name = "puppy-loving%20pacifist"

    cam = Camera()
    ws_image = ImageWebsocket("ws://localhost:8080/api/image/robot/" + name, cam)
    ws_command = CommandWebsocket("ws://localhost:8080/api/command/robot/" + name)
    decrypter = CommandDecrypter(commands)

    capture = Process(target=cam.capture)
    send = Process(target=ws_image.read_from_memory_and_send_windows)
    listen = Process(target=ws_command.receive_commands_windows)

    try:
        capture.start()
        send.start()
        listen.start()

        while 1:
            message = ws_command.receiver.recv()

            print("Main>>> Received:", message)
            print("Main>>> Command executed with result:", decrypter.decrypt_and_execute(message))

    except KeyboardInterrupt:
        pass
    finally:
        ws_image.closed.set()
        ws_command.closed.set()
        cam.image_memory.unlink()

        print("Main>>> THE END")
