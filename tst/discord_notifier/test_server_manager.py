import warnings
from unittest.mock import patch

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3

from botocore.stub import Stubber
from pytest import fixture

from discord_notifier.lib.server_manager import ServerManager
from discord_notifier.tstlib.test_mock_objects import newDescribeStacks


@fixture(params=["Running", "Stopped"])
def state(request):
    return request.param


@fixture
def cfn_client():
    cfn = boto3.client("cloudformation", region_name="us-west-2")
    stubber = Stubber(cfn)
    stubber.activate()
    with patch("boto3.client") as mock_boto3:
        mock_boto3.return_value = cfn
        yield stubber
        stubber.assert_no_pending_responses()


def set_describe_stacks_value(cfn, describe_stacks):
    expected_params = {"StackName": "StackName"}
    stack_state = describe_stacks.output
    cfn.add_response("describe_stacks", stack_state, expected_params)


def test_stop_server_started(cfn_client):
    describe_stacks = newDescribeStacks(server_state="Running")
    set_describe_stacks_value(cfn_client, describe_stacks)
    expected_params = {
        "StackName": describe_stacks.stack_name,
        "UsePreviousTemplate": True,
        "Capabilities": ["CAPABILITY_IAM"],
        "Parameters": newDescribeStacks(server_state="Stopped").parameters,
    }

    cfn_client.add_response("update_stack", {"StackId": "minecraft"}, expected_params)

    ServerManager("StackName").stop_server()


def test_stop_server_stopped(cfn_client):
    describe_stacks = newDescribeStacks(server_state="Stopped")
    set_describe_stacks_value(cfn_client, describe_stacks)
    expected_params = {
        "StackName": describe_stacks.stack_name,
        "UsePreviousTemplate": True,
        "Capabilities": ["CAPABILITY_IAM"],
        "Parameters": newDescribeStacks(server_state="Stopped").parameters,
    }

    cfn_client.add_client_error(
        "update_stack",
        service_error_code="ValidationError",
        service_message="No updates are to be performed.",
        expected_params=expected_params,
    )

    ServerManager("StackName").stop_server()
