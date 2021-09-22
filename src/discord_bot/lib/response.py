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
class MenuResponse:
    def __init__(self, type, title) -> None:
        self.type = type
        self.component_rows = []
        self.embed = Embed(title)
        self.extra_embeds = []

    def add_component_row(self):
        self.component_rows.append(ComponentRow())

    def get_response(self):
        response = {}
        response["type"] = self.type
        data = {}
        if len(self.component_rows) > 0:
            data["components"] = list(map(lambda a: a.get_value(), self.component_rows))
        data["embeds"] = [
            self.embed.get_dict(),
            *list(map(lambda a: a.get_dict(), self.extra_embeds)),
        ]
        response["data"] = data
        return response

    # stored as dict
    def add_embed(self, embed):
        self.extra_embeds.append(embed)


class Embed:
    def __init__(self, title):
        self.title = title

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


# embed with only description and color
# https://discord.com/developers/docs/resources/channel#embed-object
class BasicEmbed:
    # its a dict with fancy constructor
    def __new__(self, description, color):
        return Embed(None).with_description(description).with_color(color)
