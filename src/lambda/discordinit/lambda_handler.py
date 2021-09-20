import os

import requests

APPLICATION_ID = os.environ["ApplicationId"]
BOT_TOKEN = os.environ["BotToken"]


def lambda_handler(event, context):
    url = f"https://discord.com/api/v8/applications/{APPLICATION_ID}/commands"

    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    json = [
        {
            "name": "menu",
            "type": 1,
            "description": "summon a menu of the minecraft server",
            "options": [],
        },
        {"name": "blop", "type": 2, "description": ""},
    ]

    headers = {"Authorization": f"Bot {BOT_TOKEN}"}

    requests.post(url, headers=headers, json=json)
