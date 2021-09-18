import requests
import warnings
import os
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3

WEBHOOK_URL = os.environ['WebhookUrl']

def lambda_handler(event, context): 
    url = WEBHOOK_URL
    print(event)
    data = {
        "content" : '',
        "username" : "INSTANCEMAN"
    }

    data["embeds"] = [
        {
        "description" : 'HEY BITCHES THE SERVER IS UP',
        "title" : "MINECRAFT",
        "color" : "3066993"
        }
    ]

    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return 1
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        return 0