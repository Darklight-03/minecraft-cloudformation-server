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

    def get_component(self, custom_id):
        return [
            component
            for component in self.components
            if component.custom_id == custom_id
        ][0]

    def get_dict(self):
        return {
            "type": ComponentType.ROW,
            "components": list(map(lambda comp: comp.get_dict(), self.components)),
        }


class ButtonStyle:
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


# https://discord.com/developers/docs/interactions/message-components#buttons
class Button:
    def __init__(self, style, label=None, emoji=None, custom_id=None, disabled=None):
        self.type = ComponentType.BUTTON
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.disabled = disabled

    def get_dict(self):
        return vars(self)
