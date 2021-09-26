from discord_bot.lib.components import ComponentRow


# response types we can send
class ResponseType:
    PONG = 1
    MESSAGE = 4
    ACK = 5
    COMPONENT_ACK = 6
    COMPONENT_MESSAGE = 7


# https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
class EmbedColor:
    GREEN = 3066993
    RED = 15158332


# RESPONSES
class GenericResponse:
    ACK_RESPONSE = {"type": ResponseType.ACK}
    PONG_RESPONSE = {"type": ResponseType.PONG}


class ButtonState:
    DISABLED = True
    ENABLED = False


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-response-structure
class Response:
    def __init__(self, type) -> None:
        self.type = type
        self.component_rows = []
        self.embeds = []

    def add_component_row(self, component_row=ComponentRow()):
        if component_row is not None:
            self.component_rows.append(component_row)

    def add_embed(self, embed):
        self.embeds.append(embed)

    def get_response(self):
        response = {"type": self.type}
        data = {}
        if len(self.component_rows) > 0:
            data["components"] = list(map(lambda a: a.get_dict(), self.component_rows))
        data["embeds"] = [
            *list(map(lambda a: a.get_dict(), self.embeds)),
        ]
        response["data"] = data
        return response


# https://discord.com/developers/docs/resources/channel#embed-object
class Embed:
    def with_title(self, title):
        self.title = title
        return self

    def with_description(self, description):
        self.description = description
        return self

    def with_color(self, color):
        self.color = color
        return self

    def get_dict(self):
        return vars(self)
