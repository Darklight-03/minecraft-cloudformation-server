import os

from nacl.signing import VerifyKey
from discord_bot.lib.response import MessageResponse, ResponseType

from discord_bot.lib.server_menu import ServerMenu, SetServerState
from discord_bot.lib.request import Commands, Components, Request
from discord_bot.lib.response import GenericResponse


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

    request = Request(event.get("body-json"))
    response = ""

    # check if message is a ping
    if request.is_ping():
        return GenericResponse.PONG_RESPONSE

    if request.is_app_command():
        if request.get_command() == Commands.SERVER_MENU:
            response = ServerMenu(ResponseType.MESSAGE).run()

    if request.is_component_interaction():
        if request.user.get("id") != "105165905075396608":
            response = MessageResponse(
                ResponseType.MESSAGE,
                f"You don't have permission, {request.user.get('username')}",
            ).get_response()
        elif request.get_component() == Components.START_SERVER:
            response = SetServerState(request).run()
        elif request.get_component() == Components.STOP_SERVER:
            response = SetServerState(request).run()
        elif request.get_component() == Components.REFRESH_MENU:
            response = ServerMenu(ResponseType.COMPONENT_MESSAGE).run()
    if response == "":
        raise Exception(
            f"[INVALID_INPUT] Unrecognized request body: {event.get('body-json')}"
        )
    print(f"returning {response}")
    return response
