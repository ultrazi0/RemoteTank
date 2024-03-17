from configparser import ConfigParser


class Config:
    class CONSTANTS:
        gear_ratio = 63 + 277 / 405
        number_of_teeth = 32
        number_of_teeth_stepper = 12
        number_of_teeth_turret = 134

    class VALUES:
        turret_angle = 0.
        angle_stepper = 0.
        step = 0

        config_file_path = None
        config = ConfigParser()

        @classmethod
        def update_from_config(cls, cfg_file_path: str = None):
            # Make sure the config file is provided
            if (cfg_file_path is None) and (cls.config_file_path is None):
                raise ValueError("Config file not provided")

            # Read the values from the config file
            cls.config.read(cfg_file_path if cfg_file_path is not None else cls.config_file_path)

            # Set values as class attributes
            for key, value in cls.config['values'].items():
                if hasattr(cls, key):
                    setattr(cls, key, type(getattr(cls, key))(value))

        @classmethod
        def save_to_config(cls, cfg_file_path: str = None):
            # Make sure the config file is provided
            if (cfg_file_path is None) and (cls.config_file_path is None):
                raise ValueError("Config file not provided")

            # Check whether the field exists
            if "values" not in cls.config:
                cls.config["values"] = {}

            # Save class attributes to the config file
            for attr_name in dir(cls):
                if not attr_name.startswith("__") and not attr_name.startswith("config") \
                        and not callable(getattr(cls, attr_name)):
                    cls.config["values"][attr_name] = str(getattr(cls, attr_name))

            # Write the config to the file
            with open(cfg_file_path if cfg_file_path is not None else cls.config_file_path, "w") as config_file:
                cls.config.write(config_file)
