import warnings
from unittest.mock import patch

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3

from botocore.stub import Stubber
from pytest import fixture

from discord_notifier.lib.parameter_client import Parameter


@fixture(params=["Running", "Stopped"])
def state(request):
    return request.param


@fixture
def ssm_client():
    ssm = boto3.client("ssm", region_name="us-west-2")
    stubber = Stubber(ssm)
    stubber.activate()
    with patch("boto3.client") as mock_boto3:
        mock_boto3.return_value = ssm
        yield stubber
        stubber.assert_no_pending_responses()


def test_set_canstart(ssm_client, state):
    response = {"Version": 152, "Tier": "Standard"}
    expected_params = {
        "Name": "CanStart",
        "Value": state,
        "Overwrite": True,
        "AllowedPattern": "(True|False)",
    }

    ssm_client.add_response("put_parameter", response, expected_params)

    Parameter().set_canstart(state)
