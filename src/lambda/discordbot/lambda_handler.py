import os

from nacl.signing import VerifyKey

from discordbot.blep import blep
from discordbot.request import is_app_command, is_blep, is_ping
from discordbot.response import GenericResponse

PUBLIC_KEY = os.environ["PublicKey"]


# VERIFICATION
def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event["params"]["header"].get("x-signature-ed25519")
    auth_ts = event["params"]["header"].get("x-signature-timestamp")

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    # raises an error if unequal
    verify_key.verify(message, bytes.fromhex(auth_sig))


# CODE STARTS HERE
def lambda_handler(event, context):
    print(f"event {event}")  # debug print
    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # check if message is a ping
    body = event.get("body-json")
    if is_ping(body):
        return GenericResponse.PONG_RESPONSE

    if is_app_command(body):
        if is_blep(body):
            return blep(body)

    raise Exception(f"[INVALID_INPUT] Unrecognized request body: {body}")
