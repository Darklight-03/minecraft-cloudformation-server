import os

from nacl.signing import VerifyKey

from discord_bot.lib.commands.set_server_state import set_server_state
from discord_bot.lib.components import Components
from discord_bot.lib.request import Commands, Request
from discord_bot.lib.response import Embed, EmbedColor, GenericResponse, ResponseType
from discord_bot.lib.server import Server
from discord_bot.lib.server_menu import ServerMenu


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


ADMIN_ID = "105165905075396608"


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
            response = ServerMenu(ResponseType.MESSAGE, Server()).get_response()

    if request.is_component_interaction():
        if request.user["id"] != ADMIN_ID and request.get_component() in [
            "button_start_server"
        ]:
            # send invalid permission response if no perm
            response = (
                ServerMenu(ResponseType.COMPONENT_MESSAGE, Server())
                .add_embed(
                    (
                        Embed()
                        .with_description(
                            f"You don't have permission to {request.get_component()}, "
                            f"{request.user.get('username')}"
                        )
                        .with_color(EmbedColor.RED)
                    )
                )
                .get_response()
            )
        elif request.get_component() == Components.START_SERVER:
            response = set_server_state(request)
        elif request.get_component() == Components.STOP_SERVER:
            response = set_server_state(request)
        elif request.get_component() == Components.REFRESH_MENU:
            response = ServerMenu(
                ResponseType.COMPONENT_MESSAGE, Server()
            ).get_response()
    if response == "":
        raise Exception(
            f"[INVALID_INPUT] Unrecognized request body: {event.get('body-json')}"
        )
    print(f"returning {response}")
    return response
