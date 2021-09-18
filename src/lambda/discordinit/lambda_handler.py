import requests
import os

APPLICATION_ID = os.environ['ApplicationId']
BOT_TOKEN = os.environ['BotToken']

def lambda_handler(event, context):
    url = f"https://discord.com/api/v8/applications/{APPLICATION_ID}/commands"

    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    json = [
        {
            "name": "blep",
            "type": 1,
            "description": "A probably not working command",
            "options": [
                {
                    "name": "arg",
                    "description": "The type of blep",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "Dog",
                            "value": "dogg"
                        },
                        {
                            "name": "Krog",
                            "value": "krogg"
                        },
                        {
                            "name": "Trog",
                            "value": "trogg"
                        }
                    ]
                },
                {
                    "name": "dostuff",
                    "description": "Whether to do stuffs",
                    "type": 5,
                    "required": False
                }
            ]
        },
        {
            "name": "blop",
            "type": 2,
            "description": ""
        }
    ]

    headers = {
        "Authorization": f"Bot {BOT_TOKEN}"
    }

    r = requests.post(url, headers=headers, json=json)