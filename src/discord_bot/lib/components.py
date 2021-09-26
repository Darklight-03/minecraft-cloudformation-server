class Components:
    START_SERVER = "button_start_server"
    STOP_SERVER = "button_stop_server"
    REFRESH_MENU = "button_refresh_menu"


# component types
class ComponentType:
    ROW = 1
    BUTTON = 2
    MENU = 3


class Component:
    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def get_dict(self):
        return vars(self)


# https://discord.com/developers/docs/interactions/message-components#action-rows
class ComponentRow:
    def __init__(self):
        self.components = []

    def __iter__(self):
        return iter(self.components)

    def add_component(self, component):
        self.components.append(component)

    def get_component(self, custom_id) -> Component:
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
class Button(Component):
    def __init__(self, style, label=None, emoji=None, custom_id=None, disabled=None):
        self.type = ComponentType.BUTTON
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.disabled = disabled
