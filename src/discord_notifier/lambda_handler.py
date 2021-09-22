import boto3
import os
import warnings
from botocore.exceptions import ClientError

import requests

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)

WEBHOOK_URL = os.environ["WebhookUrl"]


def stop_server():
    cfn = boto3.client("cloudformation")
    stack_name = os.environ.get("STACK_NAME")
    stack = cfn.describe_stacks(StackName=stack_name)

    def set_state(x):
        if x.get("ParameterKey") == "ServerState":
            x["ParameterValue"] = "Stopped"
        return x

    stack_parameters = stack.get("Stacks")[-1].get("Parameters")
    stack_parameters = list(map(set_state, stack_parameters))
    try:
        cfn.update_stack(
            StackName=stack_name,
            UsePreviousTemplate=True,
            Capabilities=["CAPABILITY_IAM"],
            Parameters=stack_parameters,
        )
    except ClientError as e:
        print(e)


def lambda_handler(event, context):
    url = WEBHOOK_URL
    print(event)

    data = {"content": "", "username": "INSTANCEMAN"}

    data["embeds"] = [
        {
            "description": "HEY BITCHES THE SERVER IS UP",
            "title": "MINECRAFT",
            "color": "3066993",
        }
    ]
    if "discord_message" in event.keys():
        data["username"] = "Server Notifier"  # not sure if space allowed
        data["content"] = event["discord_message"]
        del data["embeds"]

    if "desired_state" in event.keys():
        boto3.client("ssm").put_parameter(
            Name="CanStart",
            Value="True" if event["desired_state"] == "Running" else "False",
            Overwrite=True,
            AllowedPattern="(True|False)",
        )
        if event["desired_state"] == "Stopped":
            stop_server()

    result = requests.post(url, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return 1
    else:
        print(f"Payload delivered successfully, code {result.status_code}.")
        return 0
