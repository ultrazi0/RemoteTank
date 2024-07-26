class CommandDecrypter:
    def __init__(self, command_dict: dict, message_type_key: str = "messageType",
                 function_name_key: str = "command", values_key: str = "values"):
        self.command_dict = command_dict
        self.message_type_key = message_type_key
        self.function_name_key = function_name_key
        self.values_key = values_key

    def decrypt(self, json_messages: list):
        for json_message in json_messages:
            message_is_a_command = False
            func = None
            kwargs = {}

            for key, value in json_message.items():
                if key == self.message_type_key:
                    # value is a string with message type
                    if value == self.function_name_key:
                        # message is a command
                        message_is_a_command = True

                elif key == self.function_name_key:
                    if not message_is_a_command:
                        print(
                            f"CommandDecrypter>>> Received message with a command field, but not of \"command\" type."
                            f" Message will not be parsed further"
                        )
                        break

                    # value is a string
                    if value not in self.command_dict.keys():
                        print(f"CommandDecrypter>>> No command with name \"{value}\"")
                        continue

                    func = self.command_dict[value]
                elif key == self.values_key:
                    # value is a dictionary
                    kwargs = value
                elif key == "message":
                    # value is a message
                    print(f"CommandDecrypter>>> Received message: \"{value}\"")

            if (not message_is_a_command) or (not func):
                continue
            yield func, kwargs

    def decrypt_and_execute(self, json_messages: list) -> list:
        results = []

        for func, kwargs in self.decrypt(json_messages):
            if func is None:
                results.append((False, None))
                continue

            results.append((True, func(**kwargs)))

        return results
