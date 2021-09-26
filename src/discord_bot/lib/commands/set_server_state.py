from discord_bot.lib.request import Request
from discord_bot.lib.response import ResponseType
from discord_bot.lib.server import Server
from discord_bot.lib.server_menu import ServerMenu, ServerState


def set_server_state(request: Request):
    desired_state = ServerState.get_state_from_component(request.get_component())
    server = Server()
    server.update()
    status = server.set_state(desired_state)
    response = ServerMenu(ResponseType.COMPONENT_MESSAGE, server)

    # if server already was in desired state, only disable clicked button
    if "is in UPDATE_IN_PROGRESS state" in str(status):
        response.status.title = (
            "Server is still loading, please wait for it to start/stop."
        )
    else:
        response.status.title = str(status)

    return response.get_response()
