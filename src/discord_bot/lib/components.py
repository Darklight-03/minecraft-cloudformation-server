# component types
class ComponentType:
    ROW = 1
    BUTTON = 2
    MENU = 3


# https://discord.com/developers/docs/interactions/message-components#action-rows
class ComponentRow:
    def __init__(self):
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def get_component(self, id):
        return [component for component in self.components if component.id == id][0]

    def get_value(self):
        value = {}
        value["type"] = ComponentType.ROW
        value["components"] = list(map(lambda comp: comp.get_value(), self.components))
        return value


class ButtonStyle:
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


# https://discord.com/developers/docs/interactions/message-components#buttons
class Button:
    def __init__(self, style, label="", emoji="", id="", disabled=""):
        self.style = style
        self.label = label
        self.emoji = emoji
        self.id = id
        self.disabled = disabled

    def get_value(self):
        value = {}
        value["type"] = ComponentType.BUTTON
        value["style"] = self.style
        if self.label != "":
            value["label"] = self.label
        if self.emoji != "":
            value["emoji"] = self.emoji
        if self.id != "":
            value["custom_id"] = self.id
        if self.disabled != "":
            value["disabled"] = self.disabled
        return value