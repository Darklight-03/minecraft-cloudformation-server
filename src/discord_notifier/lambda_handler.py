import boto3
import os
import warnings

import requests

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)

WEBHOOK_URL = os.environ["WebhookUrl"]


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

    result = requests.post(url, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return 1
    else:
        print(f"Payload delivered successfully, code {result.status_code}.")
        return 0
