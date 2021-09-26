from pytest import mark

from discord_bot.lib.server import ServerState


@mark.parametrize(
    "server_state,can_start,stack_state",
    [
        (ServerState.RUNNING, True, "UPDATE_IN_PROGRESS"),
        (ServerState.STOPPED, False, "UPDATE_COMPLETE"),
    ],
)
def test_server_update(server, server_state, can_start, stack_state):
    server = server(
        can_start=can_start, stack_state=stack_state, server_state=server_state
    )
    server.update()
    assert server.updated
    assert server.current_state == server_state
    assert str(server.can_start) == str(can_start)
    assert server.stack_status == stack_state


def test_server_set_state_outside_time(server):
    server = server(can_start=False)
    server.update()
    assert "time window" in str(server.set_state(ServerState.RUNNING))


@mark.parametrize("state", [ServerState.RUNNING, ServerState.STOPPED])
def test_server_set_state_to_current(server, state):
    server = server(server_state=state, stack_state="UPDATE_COMPLETE")
    server.update()
    assert f"Server is already {state.lower()}" in str(server.set_state(state))


def test_server_set_state_success(server, update_stack_value):
    server = server(server_state=ServerState.STOPPED)
    server.update()
    update_stack_value(ServerState.RUNNING)
    server.set_state(ServerState.RUNNING)


def test_server_set_state_error(server, update_stack_error):
    server = server(server_state=ServerState.STOPPED)
    server.update()
    update_stack_error(
        server_state=ServerState.RUNNING,
        error_code="ValidationError",
        error_message="No updates are to be performed.",
    )
    assert "No updates are to be performed." in str(
        server.set_state(ServerState.RUNNING)
    )
