
if __name__ == "__main__":
    from multiprocessing import Process
    from commandDecrypter import CommandDecrypter
    from camera import Camera
    from sock import ImageWebsocket, CommandWebsocket, FeedbackWebsocket


    def my_move(speed, turn):
        print(f"Main>>> I have been moved with the speed {speed} in direction {turn}")

    def my_shoot():
        print(">>> Yes, Sir! Shooting!")


    commands = {
        "MOVE": my_move,
        "SHOOT": my_shoot
    }

    cam = Camera()
    ws_image = ImageWebsocket("ws://localhost:8080/image/app/send", cam)
    ws_command = CommandWebsocket("ws://localhost:8080/command/topic")
    ws_feedback = FeedbackWebsocket("ws://localhost:8080/feedback/app/send")
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
            ws_feedback.send(f"Main>>> Received: {message}")
            print("Main>>> Command executed with result:", decrypter.decrypt_and_execute(message))

        capture.join()
        send.join()
        listen.join()
    except KeyboardInterrupt:
        pass
    finally:
        ws_image.closed.set()
        ws_command.closed.set()
        cam.image_memory.unlink()

        print("Main>>> THE END")
