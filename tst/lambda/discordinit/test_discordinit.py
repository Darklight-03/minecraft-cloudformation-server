from unittest.mock import ANY, patch

with patch("os.environ") as environ:
    from discordinit import lambda_handler


@patch("requests.put")
def test_posts_commands(put):
    lambda_handler.lambda_handler("", "")
    # Assert commands are updated
    put.assert_called_with(ANY, headers=ANY, json=ANY)
    # check that header has authorization token
    assert "Authorization" in put.call_args.kwargs.get("headers").keys()
    # Check that commands is at end of url
    assert put.call_args.args[0].split("/")[-1] == "commands"
