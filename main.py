import RPi.GPIO as GPIO


if __name__ == "__main__":

    from multiprocessing import Process
    from commandDecrypter import CommandDecrypter
    from camera import Camera
    from sock import ImageWebsocket, CommandWebsocket, FeedbackWebsocket

    from motors import Motor_PWM

    host = "192.168.2.160"

    cam = Camera()
    ws_image = ImageWebsocket(f"ws://{host}:8080/image/app/send", cam)
    ws_command = CommandWebsocket(f"ws://{host}:8080/command/topic")
    ws_feedback = FeedbackWebsocket(f"ws://{host}:8080/feedback/app/send")

    capture = Process(target=cam.capture)
    send = Process(target=ws_image.read_from_memory_and_send_windows)
    listen = Process(target=ws_command.receive_commands_windows)

    GPIO.setmode(GPIO.BOARD)

    m1 = Motor_PWM(21, 19, 'l', min_speed=20, min_activation_speed=20)
    m2 = Motor_PWM(8, 10, 'r', min_speed=20, min_activation_speed=20)


    def my_move(speed, turn):
        print(f"Main>>> I have been moved with the speed {speed} in direction {turn}")
        m1.move(speed, turn)
        m2.move(speed, turn)

    def my_shoot():
        print(">>> Yes, Sir! Shooting!")
    
    def stop():
        print("Main>>> I must stop")
        m1.stop()
        m2.stop()


    commands = {
        "MOVE": my_move,
        "SHOOT": my_shoot,
        "STOP": stop
    }

    decrypter = CommandDecrypter(commands)


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
