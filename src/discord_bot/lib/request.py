# request types we can receive
class RequestType:
    MESSAGE_PING = 1
    MESSAGE_APP = 2
    MESSAGE_COMPONENT = 3


class CommandType:
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


class Commands:
    SERVER_MENU = "menu"


class Components:
    START_SERVER = "button_start_server"
    STOP_SERVER = "button_stop_server"
    REFRESH_MENU = "button_refresh_menu"


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-structure
class Request:
    def __init__(self, input):
        self.id = input.get("id")
        self.application_id = input.get("application_id")
        self.type = input.get("type")

        # assign optional parameters to none for ease of use
        self.data = None
        self.guild_id = None
        self.channel_id = None
        self.user = None
        self.member = None
        self.token = None
        self.version = None
        self.message = None

        # set all optional parameters if they were provided
        for key in input:
            setattr(self, key, input[key])

        # user is hiding inside member if its None
        if self.user is None and self.member is not None:
            self.user = self.member["user"]

    def invalid_request(self):
        raise Exception("Invalid request type")

    # return name of command for APP type
    def get_command(self):
        if self.is_app_command():
            return self.data.get("name")
        else:
            self.invalid_request()

    def get_component(self):
        if self.is_component_interaction():
            return self.data.get("custom_id")
        else:
            self.invalid_request()

    # check request types
    def is_ping(self):
        return self.type == RequestType.MESSAGE_PING

    def is_app_command(self):
        return self.type == RequestType.MESSAGE_APP

    def is_component_interaction(self):
        return self.type == RequestType.MESSAGE_COMPONENT
