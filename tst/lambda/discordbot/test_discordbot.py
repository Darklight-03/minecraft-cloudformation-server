from unittest.mock import patch

from discordbot.components import ComponentType
from discordbot.response import ResponseType

with patch("os.environ") as environ:
    from discordbot import lambda_handler
    from discordbot.request import is_app_command, is_component_interaction, is_ping

ping_packet = {"type": 1}
application_command_packet = {"type": 2}
component_packet = {"type": 3}
PING = 1
APP = 2
COMPONENT = 3


class incoming_packet:
    def __init__(self, type, name) -> None:
        json = {}
        json["type"] = type
        data = {}
        data["name"] = name
        json["data"] = data

        self.output = {"body-json": json}


def test_ping_pong():
    assert is_ping(ping_packet) is True


def test_app_command():
    assert is_app_command(application_command_packet) is True


def test_component():
    assert is_component_interaction(component_packet) is True


def assert_component_is_valid(component):
    valid_button_keys = [
        "type",
        "custom_id",
        "disabled",
        "style",
        "label",
        "emoji",
        "url",
    ]
    valid_menu_keys = [
        "type",
        "custom_id",
        "disabled",
        "options",
        "placeholder",
        "min_values",
        "max_values",
    ]
    component_type = component["type"]
    if component_type == ComponentType.BUTTON:
        for key in component.keys():
            assert key in valid_button_keys
            valid_button_keys.remove(key)
        assert "style" not in valid_button_keys
        assert "type" not in valid_button_keys
        assert component["type"] in range(1, 6)

    elif component_type == ComponentType.MENU:
        for key in component.keys():
            assert key in valid_menu_keys
            valid_menu_keys.remove(key)
        assert "type" not in valid_menu_keys
        assert "custom_id" not in valid_menu_keys
        assert "options" not in valid_menu_keys
        # TODO assert options are actually valid
        assert type(component["options"]) is list

    else:
        assert False  # invalid component type


def assert_component_row_is_valid(row):
    valid_keys = ["type", "components"]
    assert row["type"] == ComponentType.ROW
    for key in row.keys():
        assert key in valid_keys
        valid_keys.remove(key)
    components = row["components"]
    assert type(components) is list
    for component in components:
        assert component["type"] != ComponentType.ROW
        assert_component_is_valid(component)


def assert_data_is_valid(data, response_type):
    valid_keys = ["tts", "content", "embeds", "allowed_mentions", "flags", "components"]
    assert type(data) is dict
    for key in data.keys():
        assert key in valid_keys
        valid_keys.remove(key)

    # must have content (remove this if we need one without content)
    assert "content" not in valid_keys
    if "components" in data.keys():
        components = data["components"]
        assert type(data["components"]) is list
        for item in components:
            assert_component_row_is_valid(item)


def assert_response_is_valid(response, response_type):
    assert response["type"] == response_type
    if "data" in response.keys():
        assert response_type != ResponseType.PONG
        data = response["data"]
        assert_data_is_valid(data, response_type)


@patch("discordbot.lambda_handler.verify_signature")
def test_blep(vsig):
    event = incoming_packet(APP, "blep").output
    # TODO assert lambda_handler returns correct value later
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.MESSAGE)
    vsig.assert_called_once_with(event)
