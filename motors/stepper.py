import RPi.GPIO as GPIO
from time import sleep


class Stepper:
    halfstepping = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1]
    ]

    fullstepping_power = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1]
    ]

    fullstepping_light = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

    def __init__(self, in1, in2, in3, in4, initial_angle=0., initial_step=0, initial_turret_angle=0.,
                 upper_border=None, lower_border=None, gear_ratio=(63+277/405), number_of_teeth=32,
                 number_of_teeth_stepper=None, number_of_teeth_turret=None, config=None) -> None:

        if (upper_border is not None) and (initial_angle > upper_border) and not config:
            raise ValueError("Initial angle cannot be greater than the upper border")
        if (lower_border is not None) and (initial_angle < lower_border) and not config:
            raise ValueError("Initial angle cannot be smaller than the lower border")

        self.pins = [in1, in2, in3, in4]
        # Set up pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        if config is not None:
            self.angle = config.VALUES.angle_stepper  # current angle on the motor
            self.step = config.VALUES.step  # current step
            self.gear_ratio = config.CONSTANTS.gear_ratio  # Characteristic of a motor
            self.number_of_teeth = config.CONSTANTS.number_of_teeth  # teeth INSIDE the stepper motor
            self.turret_angle = config.VALUES.turret_angle
            self.number_of_teeth_stepper = config.CONSTANTS.number_of_teeth_stepper
            self.number_of_teeth_turret = config.CONSTANTS.number_of_teeth_turret
        else:
            self.angle = initial_angle  # current angle on the motor
            self.step = initial_step  # current step
            self.gear_ratio = gear_ratio  # Characteristic of a motor
            self.number_of_teeth = number_of_teeth  # teeth INSIDE the stepper motor \ characteristic of a motor
            self.turret_angle = initial_turret_angle
            self.number_of_teeth_stepper = number_of_teeth_stepper
            self.number_of_teeth_turret = number_of_teeth_turret

        self.upper_border = upper_border
        self.lower_border = lower_border
        self.config = config  # config class
        self.time_of_the_last_turn = -1

    # Rotates stepper by a specified amount of steps
    def rotate(self, steps, method=None, delay=0.001, turn_coefficient=1) -> bool:
        if method is None:
            method = self.fullstepping_power
        steps = round(steps * turn_coefficient)

        # Method choosing -- two available
        if method == self.halfstepping:
            d_angle = 360 / (self.gear_ratio * self.number_of_teeth * 2)
        elif (method == self.fullstepping_power) or (method == self.fullstepping_light):
            d_angle = 360 / (self.gear_ratio * self.number_of_teeth)
        else:
            # If another method chosen
            raise RuntimeError('Specified method not supported')

        # Start rotating
        if steps > 0:  # Choose the direction
            for step in range(steps):

                new_angle = self.angle + d_angle  # angle after turning by 1 step

                # Cannon angle after turning by 1 step -- IF config is given
                if self.turret_angle is not None:
                    new_turret_angle = self.turret_angle + 1 / self.angle_turret(1 / d_angle)

                # Take borders into account, only upper border because here it is turning right
                if self.upper_border is not None:
                    # If stepper works as a turret, then check the turret angle
                    if self.turret_angle is not None:
                        if new_turret_angle > self.upper_border:
                            print("Cannot go any further right due to the borders")
                            return False  # Quit the function
                    else:  # Else the stepper's angle
                        if new_angle > self.upper_border:
                            print("Cannot go any further right due to the borders")
                            return False  # Quit the function

                self.step += 1  # The next step
                # Check if the full cycle has been completed --> start from the beginning
                if self.step > len(method) - 1:
                    self.step = 0

                # Set pins in the position (ON or OFF) according to the method
                for pin in range(len(self.pins)):
                    GPIO.output(self.pins[pin], method[self.step][pin])

                # Update angles
                if self.turret_angle is not None:
                    self.turret_angle = new_turret_angle
                self.angle = new_angle

                sleep(delay)  # Wait until everything is placed in position
        else:  # Turning counter-clockwise
            for step in range(-steps):  # Steps is negative --> range should be positive

                new_angle = self.angle - d_angle  # Angle decreases

                # Cannon angle after turning by 1 step -- IF config is given
                if self.turret_angle is not None:
                    new_turret_angle = self.turret_angle - 1 / self.angle_turret(1 / d_angle)

                # Take borders into account
                if self.lower_border is not None:
                    if self.turret_angle is not None:
                        if new_turret_angle < self.lower_border:
                            print("Cannot go any further left due to the borders")
                            return False
                    else:
                        if new_angle < self.lower_border:
                            print("Cannot go any further left due to the borders")
                            return False

                # Rotating in other direction, so taking steps back
                self.step -= 1
                # Check if the full cycle has been completed --> start from the beginning
                if self.step < 0:
                    self.step = len(method) - 1

                # Set pins in the position (ON or OFF) according to the method
                for pin in range(len(self.pins)):
                    GPIO.output(self.pins[pin], method[self.step][pin])

                # Update the angles
                if self.turret_angle is not None:
                    self.turret_angle = new_turret_angle
                self.angle = new_angle

                sleep(delay)  # Wait until everything is placed in position

        # Turn off all the pins so that there is no current, and hence the stepper can cool off
        for pin in range(len(self.pins)):
            GPIO.output(self.pins[pin], 0)

        self.angle = self.set_angle_between_borders(self.angle)  # Set the angle between -180 and 180
        if self.turret_angle is not None:  # Set turret angle between -180 and 180
            self.turret_angle = self.set_angle_between_borders(self.turret_angle)

        # Write down the values to config
        if self.config is not None:
            self.config.VALUES.angle_stepper = self.angle
            self.config.VALUES.step = self.step
            self.config.VALUES.turret_angle = self.turret_angle

            self.config.VALUES.save_to_config()

        return True

    # Turn stepper to a specified angle
    def turn_to(self, angle, delay=0.002, method=None):
        if method is None:
            method = self.fullstepping_light

        turn_angle = angle - self.angle  # The angle by which the stepper should be rotated

        # Calculate the needed amount of steps
        if method == self.halfstepping:
            amount_of_steps = turn_angle * (self.gear_ratio * self.number_of_teeth * 2) / 360  # For halfstepping
        elif (method == self.fullstepping_power) or (method == self.fullstepping_light):
            amount_of_steps = turn_angle * (self.gear_ratio * self.number_of_teeth) / 360  # For fullstepping
        else:
            raise TypeError("Stepper>>> Provided method not supported")

        # Rotate by that amount of steps
        self.rotate(round(amount_of_steps), method=method, delay=delay)

    # Turn stepper by a specified angle
    def turn_by(self, angle, delay=0.002, method=None):
        if method is None:
            method = self.fullstepping_light

        # Calculate the needed amount of steps
        if method == self.halfstepping:
            amount_of_steps = angle * (self.gear_ratio * self.number_of_teeth * 2) / 360  # For halfstepping
        elif (method == self.fullstepping_power) or (method == self.fullstepping_light):
            amount_of_steps = angle * (self.gear_ratio * self.number_of_teeth) / 360  # For fullstepping
        else:
            raise TypeError("Stepper>>> Provided method not supported")

        # Rotate
        self.rotate(round(amount_of_steps), method=method, delay=delay)

    def angle_turret(self, turret_angle):
        """
        Calculates the stepper angle needed to turn the turret by turret_angle

        ---Numbers of teeth can be either directly specified or read from the config file---
        """

        if (self.number_of_teeth_turret is None) or (self.number_of_teeth_stepper is None):
            raise ValueError(
                'Parameters number_of_teeth_stepper and number_of_teeth_turret have not been provided')

        return turret_angle * self.number_of_teeth_turret / self.number_of_teeth_stepper

    @staticmethod
    def set_angle_between_borders(angle):
        """Sets the angle between -180 and 180"""
        amount_of_semicircles = angle // 180
        return angle - 180 * (amount_of_semicircles + amount_of_semicircles % 2)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    from config import Config

    init_angle = Config.VALUES.angle_stepper
    init_step = Config.VALUES.step

    stepper = Stepper(11, 13, 15, 16, initial_angle=init_angle, initial_step=init_step, config=Config)

    try:
        while 1:
            try:
                inp = input('Enter angle: ')
                mode, ang = inp.split()
            except ValueError:
                mode = 'by'
                ang = inp
            angle = float(ang)

            if mode == 'by':
                stepper.turn_by(ang)
            if mode == 'to':
                stepper.turn_to(ang)

            print(stepper.angle, stepper.step)
    except KeyboardInterrupt:
        print("\nThe program closed via the Ctrl + C command")

    finally:
        print('Goodbye!')
        sleep(1)
        GPIO.cleanup()
