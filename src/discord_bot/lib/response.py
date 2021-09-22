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


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-response-structure
class MessageResponse:
    def __init__(self, type, content) -> None:
        self.type = type
        self.content = content
        self.component_rows = []
        self.embeds = []

    def add_component_row(self):
        self.component_rows.append(ComponentRow())

    def get_response(self):
        response = {}
        response["type"] = self.type
        data = {}
        data["content"] = self.content
        if len(self.component_rows) > 0:
            data["components"] = list(map(lambda a: a.get_value(), self.component_rows))
        data["embeds"] = self.embeds
        response["data"] = data
        return response

    # stored as dict
    def add_embed(self, embed):
        self.embeds.append(embed)


# embed with only description and color
# https://discord.com/developers/docs/resources/channel#embed-object
class BasicEmbed:
    # its a dict with fancy constructor
    def __new__(self, description, color):
        return {"description": description, "color": color}
