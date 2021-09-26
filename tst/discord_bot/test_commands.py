from unittest.mock import patch

from discord_bot.lib.commands.set_server_state import set_server_state
from discord_bot.lib.server import ServerState


@patch("discord_bot.lib.commands.set_server_state.ServerMenu")
def test_set_server_state(
    server_menu, server, get_component_request, update_stack_value
):
    # initializes expected calls for a server even though we aren't using this one
    server()

    update_stack_value(server_state=ServerState.RUNNING)
    request = get_component_request({"data": {"custom_id": "button_start_server"}})
    print(request.get_component())
    set_server_state(request)
    server_menu().get_response.assert_called_once()
    assert server_menu().status.title == "Server is currently starting"


@patch("discord_bot.lib.commands.set_server_state.ServerMenu")
def test_set_server_state_fail(
    server_menu, server, get_component_request, update_stack_error
):
    # initializes expected calls for a server even though we aren't using this one
    server()

    update_stack_error(
        server_state=ServerState.RUNNING, error_message="is in UPDATE_IN_PROGRESS state"
    )
    request = get_component_request({"data": {"custom_id": "button_start_server"}})
    print(request.get_component())
    set_server_state(request)
    server_menu().get_response.assert_called_once()
    assert "Server is still loading" in server_menu().status.title
