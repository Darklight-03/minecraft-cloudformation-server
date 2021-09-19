import os

from nacl.signing import VerifyKey

from lib.blep import ServerMenu, ServerState
from lib.request import Commands, Components, Request
from lib.response import GenericResponse


# VERIFICATION
def verify_signature(event):
    PUBLIC_KEY = os.environ["PublicKey"]
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
    request = Request(event.get("body-json"))

    if request.is_ping():
        return GenericResponse.PONG_RESPONSE

    if request.is_app_command():
        if request.get_command() == Commands.BLEP:
            return ServerMenu(request).run()

    if request.is_component_interaction():
        if request.get_component() == Components.START_SERVER:
            return ServerState(request).run()
        if request.get_component() == Components.STOP_SERVER:
            return ServerState(request).run()

    raise Exception(
        f"[INVALID_INPUT] Unrecognized request body: {event.get('body-json')}"
    )
