from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

import discord_bot.lambda_handler as lambda_handler
from discord_bot.lib.components import Components, ComponentType
from discord_bot.lib.request import Request
from discord_bot.lib.response import ResponseType
from discord_bot.lib.server_menu import ServerState
from discord_bot.tstlib.test_mock_objects import newDescribeStacks

ping_packet = {"type": 1}
application_command_packet = {"type": 2}
component_packet = {"type": 3}


class Parameter:
    def __new__(self, value):
        return {"Parameter": {"Value": value}}


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
        self.json["user"] = {"id": "105165905075396608", "username": "Darklight_03"}

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

    # default is me
    def with_user(self, username="User", id="98124"):
        self.userid = id
        self.username = username
        self.json["user"] = {"id": self.userid, "username": self.username}
        return self

    def with_member(self, username="User", id="98124"):
        self.userid = id
        self.username = username
        member = {}
        member["user"] = {"id": self.userid, "username": self.username}
        self.json["member"] = member

    def get_output(self):
        return {"body-json": self.json}


def test_ping_pong():
    assert Request(ping_packet).is_ping() is True


def test_app_command():
    assert Request(application_command_packet).is_app_command() is True


def test_component():
    assert Request(component_packet).is_component_interaction() is True


# maybe assert that items are the correct data type, stopped working when emoji was ""
# works fine when None is returned though so not too sure what is valid and what isn't
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

    if "components" in data.keys():
        components = data["components"]
        assert type(components) is list
        for item in components:
            assert_component_row_is_valid(item)

    # TODO assert embeds have all valid data


def assert_response_is_valid(response, response_type):
    assert response["type"] == response_type
    if "data" in response.keys():
        assert response_type != ResponseType.PONG
        data = response["data"]
        assert_data_is_valid(data, response_type)


@patch("discord_bot.lambda_handler.VerifyKey")
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


@patch("discord_bot.lambda_handler.VerifyKey")
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


@patch("discord_bot.lambda_handler.verify_signature")
def test_invalid_request_type(vsig):
    event = incoming_packet(59).get_output()
    with pytest.raises(Exception) as excinfo:
        lambda_handler.lambda_handler(event, "")
    assert "[INVALID_INPUT]" in str(excinfo)
    vsig.assert_called_once_with(event)


@patch("discord_bot.lambda_handler.verify_signature")
def test_ping(vsig):
    event = incoming_packet(PacketType.PING).get_output()
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.PONG)
    vsig.assert_called_once_with(event)


@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("discord_bot.lambda_handler.verify_signature")
def test_server_menu(vsig, client):
    client().describe_stacks.return_value = newDescribeStacks().output
    event = incoming_packet(PacketType.APP).with_name("menu").get_output()
    # TODO assert lambda_handler returns correct value later
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.MESSAGE)
    vsig.assert_called_once_with(event)


# Next time this is modified please refactor component_name input into desired_state,
# and map it to the component_name within the test later.. (or vice verse) asserting
# something should happen when component_name == expected_component is not intuitive.
#
# also don't think this function should be testing so much at once.. its shorter than
# 20 tests, but also more confusing
#
# ok we are up to 64 tests in this one function....
# it needs to be split in to one function per error type next time I touch it.
# I made it a bit more readable at least this time.
@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("discord_bot.lambda_handler.verify_signature")
@pytest.mark.parametrize("stack_status", ["UPDATE_IN_PROGRESS", "UPDATE_COMPLETE"])
@pytest.mark.parametrize("current_state", [ServerState.RUNNING, ServerState.STOPPED])
@pytest.mark.parametrize("can_start", ["True", "False"])
@pytest.mark.parametrize(
    "error_message",
    [
        "is in UPDATE_IN_PROGRESS state",
        "Unhandled ValidationError",
        "Unhandled Exception",
    ],
)
@pytest.mark.parametrize(
    "component_name", ["button_start_server", "button_stop_server"]
)
def test_start_server_error(
    vsig, client, component_name, error_message, can_start, current_state, stack_status
):
    # abandon pointless tests
    if (
        error_message == "is in UPDATE_IN_PROGRESS state"
        and stack_status != "UPDATE_IN_PROGRESS"
    ):
        return
    if (
        error_message == "No updates are to be performed"
        and stack_status == "UPDATE_IN_PROGRESS"
    ):
        return
    button_state = (
        ServerState.RUNNING
        if component_name != "button_start_server"
        else ServerState.STOPPED
    )
    if (
        error_message == "No updates are to be performed"
        and current_state == button_state
    ):
        return
    if (
        stack_status == "UPDATE_COMPLETE"
        and current_state == ServerState.get_state_from_component(component_name)
    ):
        error_message = f"Server is already {current_state.lower()}"

    client().get_parameter.return_value = Parameter(can_start)
    client().describe_stacks.return_value = newDescribeStacks(
        server_state=current_state,
        stack_status=stack_status,
    ).output
    code = "ValidationError"
    # for now test this here too since we have same logic
    if error_message == "Unhandled Exception":
        code = "OtherError"
    client().update_stack.side_effect = ClientError(
        error_response={"Error": {"Code": code, "Message": error_message}},
        operation_name="operation",
    )

    event = (
        incoming_packet(PacketType.COMPONENT)
        .with_component_name(component_name)
        .with_message({"content": "some_message"})
        .get_output()
    )
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.COMPONENT_MESSAGE)

    components = response["data"]["components"][0]["components"]
    id_list = ["button_start_server", "button_stop_server", "button_refresh_menu"]

    # order of components should never change
    component_ids = list(map(lambda c: c.get("custom_id"), components))
    assert component_ids == id_list

    # none of the components should be enabled if they were selected
    assert not any(
        c.get("custom_id") == component_name and c.get("disabled") is False
        for c in components
    )

    # when error is in this list, both state change buttons should be disabled (always)
    if error_message in ["is in UPDATE_IN_PROGRESS state"]:
        assert all(
            c.get("disabled") is True
            for c in components
            if c.get("custom_id") != "button_refresh_menu"
        )

    # when you try to change it to the current state, only the
    # current state should be disabled (2 total enabled buttons)
    # (unless outside time range)
    elif "Server is already " in error_message:
        if can_start == "True":
            assert sum(map(lambda c: c.get("disabled") is not True, components)) == 2

    # when server can't start, the output should include that.
    if can_start == "False" and component_name == "button_start_server":
        assert "time window" in response.get("data").get("embeds")[0].get("title")

    # when we don't have error specific logic the error itself should be the output
    elif "Unhandled" in error_message:
        assert error_message in response.get("data").get("embeds")[0].get("title")

    vsig.assert_called_once_with(event)


@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("discord_bot.lambda_handler.verify_signature")
@pytest.mark.parametrize(
    "component_name", ["button_start_server", "button_stop_server"]
)
def test_start_server_success(vsig, client, component_name):
    client().get_parameter.return_value = Parameter("True")
    if component_name == Components.STOP_SERVER:
        verb = "stopping"
        state = ServerState.STOPPED
        oldstate = ServerState.RUNNING
    elif component_name == Components.START_SERVER:
        verb = "starting"
        state = ServerState.RUNNING
        oldstate = ServerState.STOPPED
    client().describe_stacks.return_value = newDescribeStacks(
        server_state=oldstate
    ).output
    print(newDescribeStacks().output)

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

    # Assert start and stop are disabled on success
    components = response["data"]["components"][0]["components"]
    assert all(
        c.get("disabled") is True
        for c in components
        if c.get("custom_id") != "button_refresh_menu"
    )

    vsig.assert_called_once_with(event)
    assert f"Server is currently {verb}" in response.get("data").get("embeds")[0].get(
        "title"
    )
    desired_parameters = (
        newDescribeStacks(server_state=state).output.get("Stacks")[-1].get("Parameters")
    )
    assert (
        client().update_stack.call_args.kwargs.get("Parameters") == desired_parameters
    )


@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("discord_bot.lambda_handler.verify_signature")
@pytest.mark.parametrize("stack_status", ["UPDATE_COMPLETE", "UPDATE_IN_PROGRESS"])
@pytest.mark.parametrize("server_state", [ServerState.STOPPED, ServerState.RUNNING])
def test_refresh_menu(vsig, client, server_state, stack_status):
    client().describe_stacks.return_value = newDescribeStacks(
        server_state=server_state, stack_status=stack_status
    ).output
    event = (
        incoming_packet(PacketType.COMPONENT)
        .with_component_name("button_refresh_menu")
        .get_output()
    )
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.COMPONENT_MESSAGE)
    if stack_status == "UPDATE_COMPLETE":
        assert f"Server is currently {server_state.lower()}" in response.get(
            "data"
        ).get("embeds")[0].get("title")
    else:
        assert f"Server is currently {ServerState.verb(server_state)}" in response.get(
            "data"
        ).get("embeds")[0].get("title")
    vsig.assert_called_once_with(event)


@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("discord_bot.lambda_handler.verify_signature")
@pytest.mark.parametrize("can_start", ["True", "False"])
def test_refresh_menu_has_time_embed(vsig, client, can_start):
    client().get_parameter.return_value = Parameter(can_start)
    client().describe_stacks.return_value = newDescribeStacks().output
    event = (
        incoming_packet(PacketType.COMPONENT)
        .with_component_name("button_refresh_menu")
        .get_output()
    )
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.COMPONENT_MESSAGE)
    embeds = response["data"]["embeds"]
    if can_start == "True":
        assert any("available until" in e["description"] for e in embeds)
    else:
        assert any("available to start at" in e["description"] for e in embeds)


@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("discord_bot.lambda_handler.verify_signature")
def test_invalid_user(vsig, client):
    client().get_parameter.return_value = Parameter("True")
    client().describe_stacks.return_value = newDescribeStacks().output
    print(client)
    event = (
        incoming_packet(PacketType.COMPONENT)
        .with_component_name("button_start_server")
        .with_user()
        .get_output()
    )
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.COMPONENT_MESSAGE)
    assert any(
        "don't have permission" in e["description"] for e in response["data"]["embeds"]
    )
    vsig.assert_called_once_with(event)


@patch.dict("os.environ", {"STACK_NAME": "StackName"})
@patch("boto3.client")
@patch("discord_bot.lambda_handler.verify_signature")
def test_invalid_user_can_stop(vsig, client):
    client().get_parameter.return_value = Parameter("True")
    client().describe_stacks.return_value = newDescribeStacks().output
    event = (
        incoming_packet(PacketType.COMPONENT)
        .with_component_name("button_stop_server")
        .with_user()
        .get_output()
    )
    response = lambda_handler.lambda_handler(event, "")
    assert_response_is_valid(response, ResponseType.COMPONENT_MESSAGE)
    assert all(
        "don't have permission" not in e["description"]
        for e in response["data"]["embeds"]
    )
    vsig.assert_called_once_with(event)
