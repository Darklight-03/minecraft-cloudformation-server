def get_default_message():
    data = {"content": "", "username": "INSTANCEMAN"}
    data["embeds"] = [
        {
            "description": "HEY BITCHES THE SERVER IS UP",
            "title": "MINECRAFT",
            "color": "3066993",
        }
    ]
    return data


class MessageHandler:
    def __init__(self):
        self.message = get_default_message()

    def set_message(self, message):
        self.message["username"] = "Server Notifier"  # not sure if space allowed
        self.message["content"] = message
        del self.message["embeds"]
