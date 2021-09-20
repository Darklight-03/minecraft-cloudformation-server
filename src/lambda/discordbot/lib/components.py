# component types
class ComponentType:
    ROW = 1
    BUTTON = 2
    MENU = 3


# Components
class ComponentRow:
    def __init__(self):
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    # TODO def add_components_from_request(self, components):
    #     for component in components:
    #         if component.get("type") == ComponentType.BUTTON:
    #             self.components.append(Button(component))
    #         elif component.get("type") == ComponentType.MENU:
    #             # TODO menu not yet supported
    #             # self.components.append(Menu(component))
    #             raise Exception("menu not yet supported")
    #         else:
    #             raise Exception("unknown component type")

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


class Button:
    def __init__(self, style, label="", emoji="", id="", disabled=""):
        # TODO if type(style) is dict:
        #     self.init_from_dict(style)
        #     return
        self.style = style
        self.label = label
        self.emoji = emoji
        self.id = id
        self.disabled = disabled

    # TODO def init_from_dict(self, dictionary):
    #     self.label = ""
    #     self.emoji = ""
    #     self.id = ""
    #     self.disabled = ""
    #     for key in dictionary:
    #         setattr(self, key, dictionary[key])

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
