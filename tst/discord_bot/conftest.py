import os
import warnings
from unittest.mock import patch

from pytest import fixture

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3

from botocore.stub import Stubber

import discord_bot.tstlib.test_mock_objects as test_constants
from discord_bot.lib.components import Button, ButtonStyle, ComponentRow
from discord_bot.lib.request import CommandType, Request, RequestType
from discord_bot.lib.response import Embed, ResponseType
from discord_bot.lib.server import Server
from discord_bot.lib.server_menu import ServerMenu
from discord_bot.tstlib.test_mock_objects import newDescribeStacks, newGetItem


@fixture(autouse=True)
def environs():
    os.environ["STACK_NAME"] = test_constants.STACK_NAME
    os.environ["START_SCHEDULE"] = "(0 20 * * ? *)"
    os.environ["STOP_SCHEDULE"] = "(0 3 * * ? *)"
    os.environ["TABLE_NAME"] = test_constants.TABLE_NAME


@fixture
def ping_request():
    simple_ping = {
        "id": "id",
        "application_id": "application_id",
        "type": RequestType.MESSAGE_PING,
    }
    return Request(simple_ping)


@fixture
def get_app_command_request():
    def get_command(additional_parameters={}):
        simple_command = {
            "id": "id",
            "application_id": "application_id",
            "type": RequestType.MESSAGE_APP,
            "data": {"id": "id", "name": "name", "type": CommandType.CHAT_INPUT},
        }
        return Request({**simple_command, **additional_parameters})

    return get_command


@fixture
def get_component_request():
    def get_component(additional_parameters={}):
        simple_component = {
            "id": "id",
            "application_id": "application_id",
            "type": RequestType.MESSAGE_COMPONENT,
            "data": {"custom_id": "custom_id"},
        }
        return Request({**simple_component, **additional_parameters})

    return get_component


@fixture
def embed():
    return (
        Embed().with_title("title").with_color("color").with_description("description")
    )


@fixture
def emoji():
    # eventually should make an emoji object if we ever use this functionality
    return {"name": "name", "id": "891064634054942740", "animated": False}


@fixture
def button(button_factory):
    return button_factory()


@fixture
def button_factory(emoji):
    def get_button(custom_id="custom_id"):
        return Button(
            ButtonStyle.PRIMARY,
            label="label",
            emoji=emoji,
            custom_id=custom_id,
            disabled=False,
        )

    return get_button


@fixture
def component_row_with_button(button):
    row = ComponentRow()
    row.add_component(button)
    return row


@fixture
def component_row_with_buttons(button_factory):
    row = ComponentRow()
    row.add_component(button_factory("1"))
    row.add_component(button_factory("2"))
    row.add_component(button_factory("3"))
    return row


@fixture
def ssm():
    ssm = boto3.client("ssm", region_name="us-west-2")
    with Stubber(ssm) as stubber:
        stubber.activate()
        with patch("discord_bot.lib.provider.provide_ssm_client") as ssm_client:
            ssm_client.return_value = ssm
            yield stubber
            stubber.assert_no_pending_responses()


@fixture
def cfn():
    cfn = boto3.client("cloudformation", region_name="us-west-2")
    with Stubber(cfn) as stubber:
        stubber.activate()
        with patch("discord_bot.lib.provider.provide_cfn_client") as cfn_client:
            cfn_client.return_value = cfn
            yield stubber
            stubber.assert_no_pending_responses()


@fixture
def ddb():
    ddb = boto3.client("dynamodb", region_name="us-west-2")
    with Stubber(ddb) as stubber:
        stubber.activate()
        with patch("discord_bot.lib.provider.provide_ddb_client") as ddb_client:
            ddb_client.return_value = ddb
            yield stubber
            stubber.assert_no_pending_responses()


@fixture
def get_item_value(ddb):
    def get_item_factory(ecs_status="SERVICE_STEADY_STATE", instance_status="running"):
        get_item = newGetItem(
            ecs_status=ecs_status, instance_status=instance_status.lower()
        )
        expected_params = {
            "Key": {"StackName": {"S": test_constants.STACK_NAME}},
            "TableName": test_constants.TABLE_NAME,
        }
        ddb.add_response("get_item", get_item.output, expected_params)

    return get_item_factory


@fixture
def can_start_value(ssm):
    def get_parameter_can_start_factory(value="True"):
        get_can_start = {
            "Parameter": {"Name": "CanStart", "Type": "String", "Value": value}
        }
        ssm.add_response("get_parameter", get_can_start, {"Name": "CanStart"})

    return get_parameter_can_start_factory


@fixture
def describe_stacks_value(cfn):
    def describe_stacks_factory(server_state="Stopped", stack_state="UPDATE_COMPLETE"):
        describe_stacks = newDescribeStacks(
            server_state=server_state, stack_status=stack_state
        )
        expected_params = {"StackName": test_constants.STACK_NAME}
        stack_state = describe_stacks.output
        cfn.add_response("describe_stacks", stack_state, expected_params)

    return describe_stacks_factory


@fixture
def update_stack_value(cfn):
    def update_stack_factory(server_state="Running"):
        expected_params = {
            "StackName": test_constants.STACK_NAME,
            "UsePreviousTemplate": True,
            "Capabilities": ["CAPABILITY_IAM"],
            "Parameters": newDescribeStacks(server_state=server_state).parameters,
        }
        cfn.add_response(
            "update_stack", {"StackId": test_constants.STACK_NAME}, expected_params
        )

    return update_stack_factory


@fixture
def update_stack_error(cfn):
    def update_stack_error_factory(
        server_state="Running",
        error_message="No updates are to be performed.",
        error_code="ValidationError",
    ):
        expected_params = {
            "StackName": test_constants.STACK_NAME,
            "UsePreviousTemplate": True,
            "Capabilities": ["CAPABILITY_IAM"],
            "Parameters": newDescribeStacks(server_state=server_state).parameters,
        }
        cfn.add_client_error(
            "update_stack",
            service_error_code=error_code,
            service_message=error_message,
            expected_params=expected_params,
        )

    return update_stack_error_factory


@fixture
def server(cfn, ssm, can_start_value, describe_stacks_value):
    def server_factory(
        can_start=True, server_state="Stopped", stack_state="UPDATE_COMPLETE"
    ):
        describe_stacks_value(server_state=server_state, stack_state=stack_state)
        can_start_value(str(can_start))
        return Server()

    return server_factory


@fixture
def server_menu_factory(server):
    def get_server_menu(
        server_state="Stopped", stack_state="UPDATE_COMPLETE", can_start=True
    ):
        srv = server(
            server_state=server_state, can_start=can_start, stack_state=stack_state
        )
        return ServerMenu(ResponseType.COMPONENT_MESSAGE, srv)

    return get_server_menu
