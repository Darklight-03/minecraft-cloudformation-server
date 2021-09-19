from copy import deepcopy
from unittest.mock import patch

import lambda_handler
import pytest
from lib.components import ComponentType
from lib.request import Components, Request
from lib.response import ResponseType

ping_packet = {"type": 1}
application_command_packet = {"type": 2}
component_packet = {"type": 3}


def new_row(components):
    return {"type": ComponentType.ROW, "components": components}


def new_button(name):
    return {"type": ComponentType.BUTTON, "style": 1, "custom_id": name}


class PacketType:
    PING = 1
    APP = 2
    COMPONENT = 3


class incoming_packet:
    def __init__(self, type) -> None:
        self.json = {}
        self.type = type
        self.json["type"] = type
        self.data = {}
        self.json["data"] = {}

    def with_name(self, name):
        self.name = name
        self.json["data"]["name"] = name
        return self

    def with_component_name(self, name):
        self.component_name = name
        self.json["data"]["custom_id"] = name
        return self

    def with_message(self, message):
        self.message = message
        self.json["message"] = message
        return self

    def get_output(self):
        return {"body-json": self.json}


def test_ping_pong():
    assert Request(ping_packet).is_ping() is True


def test_app_command():
    assert Request(application_command_packet).is_app_command() is True


def test_component():
    assert Request(component_packet).is_component_interaction() is True


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


@patch("lambda_handler.VerifyKey")
@patch.dict("os.environ", {"PublicKey": "cf8db450"})
def test_verify_signature_fails(verify_key):
    verify_key().verify.side_effect = Exception()
    with pytest.raises(Exception) as excinfo:
        lambda_handler.lambda_handler(
            {
                "rawBody": "body",
                "params": {
                    "header": {
                        "x-signature-ed25519": "cf8db450",
                        "x-signature-timestamp": "timestamp",
                    }
                },
            },
            "",
        )
    assert "[UNAUTHORIZED]" in str(excinfo)
    verify_key.assert_called()
    verify_key().verify.assert_called_once()


@patch("lambda_handler.VerifyKey")
@patch.dict("os.environ", {"PublicKey": "cf8db450"})
def test_verify_signature(verify_key):
    lambda_handler.verify_signature(
        {
            "rawBody": "body",
            "params": {
                "header": {
                    "x-signature-ed25519": "cf8db450",
                    "x-signature-timestamp": "timestamp",
                }
            },
        }
    )
    verify_key.assert_called_once()
    verify_key().verify.assert_called_once()


@patch("lambda_handler.verify_signature")
def test_invalid_request_type(vsig):
    event = incoming_packet(59).get_output()
    # TODO assert lambda_handler returns correct value later
    with pytest.raises(Exception) as excinfo:
        lambda_handler.lambda_handler(event, "")
    assert "[INVALID_INPUT]" in str(excinfo)
    vsig.assert_called_once_with(event)


@patch("lambda_handler.verify_signature")
def test_ping(vsig):
    event = incoming_packet(PacketType.PING).get_output()
    # TODO assert lambda_handler returns correct value later
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.PONG)
    vsig.assert_called_once_with(event)


@patch("lambda_handler.verify_signature")
def test_server_menu(vsig):
    event = incoming_packet(PacketType.APP).with_name("blep").get_output()
    # TODO assert lambda_handler returns correct value later
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.MESSAGE)
    vsig.assert_called_once_with(event)


@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("lambda_handler.verify_signature")
@pytest.mark.parametrize(
    "component_name", ["button_start_server", "button_stop_server"]
)
def test_start_server(vsig, client, component_name):

    parameters = [
        {"ParameterKey": v, "ParameterValue": v}
        for v in [
            "param1",
            "param2",
            "param3",
            "param4",
            "ServerState",
            "param5",
        ]
    ]
    client().describe_stacks.return_value = {
        "Stacks": [{"Parameters": deepcopy(parameters)}]
    }

    event = (
        incoming_packet(PacketType.COMPONENT)
        .with_component_name(component_name)
        .with_message(
            {
                "content": "some_message",
                "components": [new_row([new_button("start"), new_button("stop")])],
            }
        )
        .get_output()
    )
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.COMPONENT_MESSAGE)
    vsig.assert_called_once_with(event)
    if component_name == Components.STOP_SERVER:
        parameters[4]["ParameterValue"] = "Stopped"
    if component_name == Components.START_SERVER:
        parameters[4]["ParameterValue"] = "Running"
    assert client().update_stack.call_args.kwargs.get("Parameters") == parameters
