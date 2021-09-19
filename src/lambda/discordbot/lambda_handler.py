import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3

import os

from nacl.signing import VerifyKey

PUBLIC_KEY = os.environ['PublicKey']
PING_PONG = {"type": 1}

RESPONSE_TYPES = {
                    "PONG": 1,
                    "ACK_NO_SOURCE": 2,
                    "MESSAGE_NO_SOURCE": 3,
                    "MESSAGE_WITH_SOURCE": 4,
                    "ACK_WITH_SOURCE": 5
                 }
MESSAGE_PING = 1
MESSAGE_APP = 2
MESSAGE_COMPONENT = 3


# RESPONSES
BLEP = {"type": 5}


# VERIFICATION
def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts = event['params']['header'].get('x-signature-timestamp')

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    # raises an error if unequal
    verify_key.verify(message, bytes.fromhex(auth_sig))


# CONDITIONS
def ping_pong(body):
    return body.get("type") == MESSAGE_PING


def app_command(body):
    return body.get("type") == MESSAGE_APP


def component_interaction(body):
    return body.get("type") == MESSAGE_COMPONENT


def blep(body):
    return body.get("data").get("name") == "blep"


# COMMANDS?

# may want to do this in new lambda function if take too long (probably)
def start_server():
    cfn = boto3.client('cloudformation')
    stack = cfn.describe_stacks(
        StackName="${AWS::StackName}"
    )
    parameters = stack.get("Stacks")[0].get("Parameters")

    def set_state(x):
        if x.get("ParameterKey") == "ServerState":
            x["ParameterValue"] = "Started"
        return x
    parameters = list(map(set_state, parameters))
    cfn.update_stack(
        StackName="${AWS::StackName}",
        UsePreviousTemplate=True,
        Capabilities=['CAPABILITY_IAM'],
        Parameters=parameters
    )


# CODE STARTS HERE
def lambda_handler(event, context):
    print(f"event {event}")  # debug print
    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # check if message is a ping
    body = event.get('body-json')
    if ping_pong(body):
        return PING_PONG

    if app_command(body):
        if blep(body):
            # start_server()
            return BLEP

    # dummy return
    return {
            "type": RESPONSE_TYPES['MESSAGE_NO_SOURCE'],
            "data": {
                "tts": False,
                "content": "BEEP BOOP",
                "embeds": [],
                "allowed_mentions": []
            }
        }
