from lib.components import ComponentRow


# response types we can send
class ResponseType:
    PONG = 1
    MESSAGE = 4
    ACK = 5
    COMPONENT_ACK = 6
    COMPONENT_MESSAGE = 7


# RESPONSES
class GenericResponse:
    ACK_RESPONSE = {"type": ResponseType.ACK}
    PONG_RESPONSE = {"type": ResponseType.PONG}


class MessageResponse:
    def __init__(self, type, content) -> None:
        self.type = type
        self.content = content
        self.component_rows = []

    def add_component_row(self):
        self.component_rows.append(ComponentRow())

    def add_components_from_request(self, components):
        for row in components:
            new_row = ComponentRow()
            new_row.add_components_from_request(row.get("components"))
            self.component_rows.append(new_row)

    def get_response(self):
        response = {}
        response["type"] = self.type
        data = {}
        data["content"] = self.content
        if len(self.component_rows) > 0:
            data["components"] = list(map(lambda a: a.get_value(), self.component_rows))
        response["data"] = data
        return response
