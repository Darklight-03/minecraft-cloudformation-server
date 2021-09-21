from unittest.mock import ANY, patch
import requests

with patch("os.environ") as environ:
    from discord_notifier import lambda_handler

expected_message = {
    "content": "",
    "username": "INSTANCEMAN",
    "embeds": [
        {
            "description": "HEY BITCHES THE SERVER IS UP",
            "title": "MINECRAFT",
            "color": "3066993",
        }
    ],
}


@patch("requests.post")
def test_delivers_webhook(post):
    assert lambda_handler.lambda_handler("", "") == 0
    # check that expected message is delivered to webhook url
    post.assert_called_once_with(ANY, json=expected_message)
    post().raise_for_status.assert_called_once()


# I don't know what this error means, but we test that it has the correct result
@patch("requests.post")
def test_HTTPerror(post):
    post().raise_for_status.side_effect = requests.exceptions.HTTPError()
    assert lambda_handler.lambda_handler("", "") == 1
    post.assert_called_with(ANY, json=expected_message)
    post().raise_for_status.assert_called()
    # why is setting up the side_effect count as a call, I can't assert called_once_with
