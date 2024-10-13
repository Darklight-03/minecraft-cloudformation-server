from unittest.mock import ANY, MagicMock, patch

import pytest
import requests

from discord_notifier.tstlib.test_mock_objects import newDescribeStacks

with patch("os.environ") as environ:
    from discord_notifier import lambda_handler

expected_message = {
    "content": "",
    "username": "INSTANCEMAN",
    "embeds": [
        {
            "description": "HEY BITCHES THE SERVER IS UP",
            "title": "MINECRAFT",
            "color": "3066993",
        }
    ],
}


class Event:
    def __init__(self):
        self.value = {}

    def with_state(self, state):
        self.value["desired_state"] = state
        return self

    def with_can_start(self, can_start):
        self.value["can_start"] = can_start
        return self


class KeyValue:
    def __init__(self, k, v):
        self.k = k
        self.v = v


class DictWhereKeyContainsStr(KeyValue):
    def __eq__(self, dict):
        return self.v in dict[self.k]


MockPost = MagicMock()
MockBoto3Client = MagicMock()
Dynamo = MagicMock()


@patch("boto3.client", new=MockBoto3Client)
@patch("requests.post", new=MockPost)
@patch("discord_notifier.lambda_handler.Dynamo", new=Dynamo)
class TestDiscordNotifier:
    def teardown_method(self, test_method):
        MockBoto3Client.reset_mock()
        MockPost.reset_mock()
        Dynamo.reset_mock()

    @pytest.mark.parametrize("can_start", ["True", "False"])
    def test_sets_can_start(self, can_start):
        assert (
            lambda_handler.lambda_handler(Event().with_can_start(can_start).value, "")
            == 0
        )
        MockBoto3Client().put_parameter.assert_called_once_with(
            Name="CanStart",
            Value=can_start,
            AllowedPattern="(True|False)",
            Overwrite=True,
        )

    @pytest.mark.parametrize("desired_state", ["Stopped"])
    def test_changes_server_state(self, desired_state):
        MockBoto3Client().describe_stacks.return_value = newDescribeStacks(
            server_state="Running"
        ).output

        assert (
            lambda_handler.lambda_handler(Event().with_state(desired_state).value, "")
            == 0
        )

        desired_parameters = (
            newDescribeStacks(server_state="Stopped")
            .output.get("Stacks")[-1]
            .get("Parameters")
        )
        if desired_state == "Stopped":
            assert (
                MockBoto3Client().update_stack.call_args.kwargs.get("Parameters")
                == desired_parameters
            )

    def test_delivers_custom_message(self):
        assert (
            lambda_handler.lambda_handler({"discord_message": "custom_message"}, "")
            == 0
        )

        MockPost.assert_called_once_with(
            ANY, json=DictWhereKeyContainsStr("content", "custom_message")
        )
        MockPost().raise_for_status.assert_called_once()

    def test_ec2instance_statechange_event(self, ec2_instance_statechange_event):
        assert lambda_handler.lambda_handler(ec2_instance_statechange_event, "") == 0
        Dynamo().put_instance_status.assert_called_once()

    def test_ecs_statechange_event(self, ecs_statechange_event):
        assert lambda_handler.lambda_handler(ecs_statechange_event, "") == 0
        Dynamo().put_ecs_status.assert_called_once()

    def test_asg_statechange_event(self, asg_statechange_event):
        assert lambda_handler.lambda_handler(asg_statechange_event, "") == 0
        Dynamo().put_instance_status.assert_called_once()

    def test_no_message(self):
        assert lambda_handler.lambda_handler({}, "") == 0
        # check that no message is delivered to webhook url without parameters
        MockPost.assert_not_called()

    # I don't know what this error means, but we test that it has the correct result
    def test_HTTPerror(self):
        MockPost().raise_for_status.side_effect = requests.exceptions.HTTPError()
        assert (
            lambda_handler.lambda_handler({"discord_message": "custom_message"}, "")
            == 1
        )
        MockPost.assert_called_with(ANY, json=ANY)
        MockPost().raise_for_status.assert_called()
