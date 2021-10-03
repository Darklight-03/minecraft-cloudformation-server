import os
import warnings

import requests

from discord_notifier.lib.message_handler import MessageHandler
from discord_notifier.lib.parameter_client import Parameter
from discord_notifier.lib.server_manager import ServerManager

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)

WEBHOOK_URL = os.environ["WebhookUrl"]
STACK_NAME = os.environ.get("STACK_NAME")


def lambda_handler(event, context):
    print(f"event {event}")
    url = WEBHOOK_URL
    stack_name = STACK_NAME
    send_message = False

    message_handler = MessageHandler()

    if "discord_message" in event.keys():
        send_message = True
        message_handler.set_message(event["discord_message"])

    if "can_start" in event.keys():
        can_start = event["can_start"]
        Parameter().set_canstart(can_start)

    if "desired_state" in event.keys():
        desired_state = event["desired_state"]
        if desired_state == "Stopped":
            cfn = ServerManager(stack_name)
            cfn.stop_server()

    if send_message:
        result = requests.post(url, json=message_handler.message)

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            return 1
        else:
            print(f"Payload delivered successfully, code {result.status_code}.")
            return 0

    else:
        return 0
