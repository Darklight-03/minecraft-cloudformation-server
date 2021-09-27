from datetime import datetime
from unittest.mock import patch

from pytest import mark

from discord_bot.lib.components import Components
from discord_bot.lib.response import EmbedColor
from discord_bot.lib.server import ServerState


@mark.parametrize("server_state", [ServerState.RUNNING, ServerState.STOPPED])
def test_current_state_is_disabled(server_menu_factory, server_state):
    server_menu = server_menu_factory(
        server_state=server_state, stack_state="UPDATE_COMPLETE", can_start=True
    )
    components = server_menu.get_response()["data"]["components"][0]["components"]
    print(components)
    assert all(
        component["disabled"] is True
        for component in components
        if ServerState.get_state_from_component(component["custom_id"]) == server_state
    )
    assert server_menu.status.color == EmbedColor.GREEN


@mark.parametrize("server_state", [ServerState.RUNNING, ServerState.STOPPED])
@mark.parametrize("can_start", [True, False])
def test_server_changing_states_disables_both_buttons(
    server_menu_factory, server_state, can_start
):
    server_menu = server_menu_factory(
        server_state=server_state, stack_state="UPDATE_IN_PROGRESS", can_start=can_start
    )
    components = server_menu.get_response()["data"]["components"][0]["components"]
    print(components)
    assert all(
        component["disabled"] is True
        for component in components
        if ServerState.get_state_from_component(component["custom_id"]) is not None
    )
    assert (
        f"Server is currently {ServerState.verb(server_state)}"
        in server_menu.status.title
    )


@mark.parametrize("server_state", [ServerState.RUNNING, ServerState.STOPPED])
def test_cant_start_disables_start(server_menu_factory, server_state):
    server_menu = server_menu_factory(
        server_state=server_state, stack_state="UPDATE_COMPLETE", can_start=False
    )
    components = server_menu.get_response()["data"]["components"][0]["components"]
    print(components)
    assert all(
        component["disabled"] is True
        for component in components
        if ServerState.get_state_from_component(component["custom_id"])
        is ServerState.RUNNING
    )
    assert server_menu.status.color == EmbedColor.RED


def test_response_is_valid(server_menu_factory):
    server_menu = server_menu_factory()
    response = server_menu.response
    assert len(response.embeds) > 0
    assert len(response.component_rows) > 0
    component_iter = iter(response.component_rows[0])
    assert next(component_iter).custom_id == Components.START_SERVER
    assert next(component_iter).custom_id == Components.STOP_SERVER
    assert next(component_iter).custom_id == Components.REFRESH_MENU


@patch("discord_bot.lib.server_menu.get_current_time")
def test_schedule_works(dt, server_menu_factory):
    dt.return_value = datetime(2021, 9, 27, 4, 0, 0)
    server_menu = server_menu_factory()
    response = server_menu.get_next_start_time()
    assert response == "2021-09-27 15:00:00"
    response = server_menu.get_next_stop_time()
    assert response == "2021-09-27 22:00:00"
