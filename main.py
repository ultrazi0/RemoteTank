import RPi.GPIO as GPIO

from camera import Camera
from sock import ImageWebsocket, CommandWebsocket, FeedbackWebsocket
from motors import Motor_PWM, Servo, Stepper


class Robot:
    def __init__(self, host: str = "192.168.2.160", config=None):
        self.cam = Camera()
        self.ws_image = ImageWebsocket(f"ws://{host}:8080/image/app/send", self.cam)
        self.ws_command = CommandWebsocket(f"ws://{host}:8080/command/topic")
        self.ws_feedback = FeedbackWebsocket(f"ws://{host}:8080/feedback/app/send")

        self.motors = []
        self.servo = None
        self.stepper = None

        self.config = config

    def initialize_motor(self, pinA, pinB, side, min_speed=0, min_activation_speed=None):
        self.motors.append(Motor_PWM(pinA, pinB, side, min_speed, min_activation_speed))

    def initialize_servo(self, pin, dy=3.5, r=7.5, start_angle=36, lower_border=None, upper_border=None,
                         min_pulse_width=1 / 1000, max_pulse_width=2.5 / 1000,
                         frame_width=20 / 1000, initial_angle=None, pin_factory=None):
        self.servo = Servo(pin, dy, r, start_angle=start_angle, lower_border=lower_border, upper_border=upper_border,
                           min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width, frame_width=frame_width,
                           initial_angle=initial_angle, pin_factory=pin_factory)

    def initialize_stepper(self, in1, in2, in3, in4, initial_angle=0., initial_step=0, initial_turret_angle=0.,
                           upper_border=None, lower_border=None, gear_ratio=(63 + 277 / 405), number_of_teeth=32,
                           number_of_teeth_stepper=None, number_of_teeth_turret=None):
        self.stepper = Stepper(in1, in2, in3, in4, initial_angle=initial_angle,
                               initial_step=initial_step, initial_turret_angle=initial_turret_angle,
                               upper_border=upper_border, lower_border=lower_border, gear_ratio=gear_ratio,
                               number_of_teeth=number_of_teeth, number_of_teeth_stepper=number_of_teeth_stepper,
                               number_of_teeth_turret=number_of_teeth_turret, config=self.config)

    def move(self, speed, turn):
        for motor in self.motors:
            motor.move(speed, turn)

    def stop(self):
        for motor in self.motors:
            motor.stop()

    def move_turret(self, tilt, turn):
        self.servo.rotate_by(tilt, turn_coefficient=10)
        self.stepper.rotate(turn, turn_coefficient=100, delay=0.002)


if __name__ == "__main__":

    from multiprocessing import Process
    from commandDecrypter import CommandDecrypter
    from config import Config

    robot = Robot(config=Config)

    capture = Process(target=robot.cam.capture)
    send = Process(target=robot.ws_image.read_from_memory_and_send_windows)
    listen = Process(target=robot.ws_command.receive_commands_windows)

    GPIO.setmode(GPIO.BOARD)

    robot.initialize_motor(21, 19, 'l', min_speed=20, min_activation_speed=20)
    robot.initialize_motor(8, 10, 'r', min_speed=20, min_activation_speed=20)

    robot.initialize_servo(24, lower_border=None, upper_border=None, dy=3.5, r=7.5, start_angle=52, initial_angle=0)

    robot.initialize_stepper(11, 13, 15, 16, number_of_teeth_stepper=12, number_of_teeth_turret=134)

    def my_shoot():
        print(">>> Yes, Sir! Shooting!")


    commands = {
        "MOVE": robot.move,
        "TURRET": robot.move_turret,
        "SHOOT": my_shoot,
        "STOP": robot.stop
    }

    decrypter = CommandDecrypter(commands)

    try:
        capture.start()
        send.start()
        listen.start()

        while 1:
            message = robot.ws_command.receiver.recv()

            print("Main>>> Received:", message)
            robot.ws_feedback.send(f"Main>>> Received: {message}")
            print("Main>>> Command executed with result:", decrypter.decrypt_and_execute(message))

        capture.join()
        send.join()
        listen.join()
    except KeyboardInterrupt:
        pass
    finally:
        robot.ws_image.closed.set()
        robot.ws_command.closed.set()
        robot.cam.image_memory.unlink()

        print("Main>>> THE END")
