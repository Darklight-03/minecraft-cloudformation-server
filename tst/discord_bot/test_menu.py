from datetime import datetime
from unittest.mock import patch

from pytest import mark

from discord_bot.lib.components import Components
from discord_bot.lib.response import EmbedColor
from discord_bot.lib.server import ServerState


@mark.parametrize("server_state", [ServerState.RUNNING, ServerState.STOPPED])
def test_current_state_is_disabled(
    ddb, server_menu_factory, server_state, get_item_value
):
    get_item_value(instance_status=server_state)
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
    ddb, server_menu_factory, server_state, can_start, get_item_value
):
    get_item_value(instance_status=server_state)
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
def test_cant_start_disables_start(
    ddb, server_menu_factory, server_state, get_item_value
):
    get_item_value(instance_status=server_state)
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


def test_response_is_valid(ddb, server_menu_factory, get_item_value):
    get_item_value()
    server_menu = server_menu_factory()
    response = server_menu.response
    assert len(response.embeds) > 0
    assert len(response.component_rows) > 0
    component_iter = iter(response.component_rows[0])
    assert next(component_iter).custom_id == Components.START_SERVER
    assert next(component_iter).custom_id == Components.STOP_SERVER
    assert next(component_iter).custom_id == Components.REFRESH_MENU


@mark.parametrize("server_state", [ServerState.RUNNING, ServerState.STOPPED])
def test_response_contains_ecs_status(
    ddb, server_menu_factory, get_item_value, server_state
):
    ecs_status = "SomeStatus55383"
    get_item_value(instance_status=server_state.lower(), ecs_status=ecs_status)
    server_menu = server_menu_factory()
    status = server_menu.status.description
    if server_state == ServerState.RUNNING:
        assert ecs_status in status
    else:
        assert ecs_status not in status


@patch("discord_bot.lib.server_menu.get_current_time")
def test_schedule_works(dt, ddb, server_menu_factory, get_item_value):
    dt.return_value = datetime(2021, 9, 27, 4, 0, 0)
    get_item_value()
    server_menu = server_menu_factory()
    response = server_menu.get_next_start_time()
    assert response == "<t:1632780000:R>"
    response = server_menu.get_next_stop_time()
    assert response == "<t:1632805200:R>"  # TODO parse and assert instead.
