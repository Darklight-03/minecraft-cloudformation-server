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
    BLEP = "blep"


class Components:
    START_SERVER = "button_start_server"
    STOP_SERVER = "button_stop_server"
    REFRESH_MENU = "button_refresh_menu"


class Request:
    def __init__(self, input):
        self.id = input.get("id")
        self.application_id = input.get("application_id")
        self.type = input.get("type")
        if "data" in input.keys():
            self.data = input.get("data")
        if "guild_id" in input.keys():
            self.guild_id = input.get("guild_id")
        if "channel_id" in input.keys():
            self.channel_id = input.get("channel_id")
        if "member" in input.keys():
            self.user = input.get("member")
        if "user" in input.keys():
            self.user = input.get("user")
        if "token" in input.keys():
            self.token = input.get("token")
        if "version" in input.keys():
            self.version = input.get("version")
        if "message" in input.keys():
            self.message = input.get("message")

    def invalidRequestTypeException():
        raise Exception("Invalid request type")

    # return name of command for APP type
    def get_command(self):
        if self.is_app_command:
            return self.data.get("name")
        else:
            self.invalidRequestTypeException()

    def get_component(self):
        if self.is_component_interaction:
            return self.data.get("custom_id")
        else:
            self.invalidRequestTypeException()

    # check request types
    def is_ping(self):
        return self.type == RequestType.MESSAGE_PING

    def is_app_command(self):
        return self.type == RequestType.MESSAGE_APP

    def is_component_interaction(self):
        return self.type == RequestType.MESSAGE_COMPONENT
