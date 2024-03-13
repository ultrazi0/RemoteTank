class CommandDecrypter:
    def __init__(self, command_dict: dict, function_name_key: str = "command", values_key: str = "values"):
        self.command_dict = command_dict
        self.function_name_key = function_name_key
        self.values_key = values_key

    def decrypt(self, json_messages: list) -> tuple:
        for json_message in json_messages:
            func = None
            kwargs = {}

            for key, value in json_message.items():
                if key == self.function_name_key:
                    # value is a string
                    if value not in self.command_dict.keys():
                        print(f"CommandDecrypter>>> No command with name \"{value}\"")
                        continue

                    func = self.command_dict[value]
                elif key == self.values_key:
                    # value is a dictionary
                    kwargs = value

            yield func, kwargs

    def decrypt_and_execute(self, json_messages: list) -> list:
        results = []

        for func, kwargs in self.decrypt(json_messages):
            if func is None:
                results.append((False, None))
                continue

            results.append((True, func(**kwargs)))

        return results
