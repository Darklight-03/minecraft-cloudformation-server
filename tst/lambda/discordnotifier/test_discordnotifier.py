import pytest
from unittest.mock import patch, ANY
with patch('os.environ') as environ:
    from discordnotifier import lambda_handler

expected_message = {
    "content" : '',
    "username" : "INSTANCEMAN",
    "embeds" : [{
        "description" : 'HEY BITCHES THE SERVER IS UP',
        "title" : "MINECRAFT",
        "color" : "3066993"
    }]
}

@patch('requests.post')
def test_delivers_webhook(post):
    assert lambda_handler.lambda_handler("", "") == 0
    # check that expected message is delivered to webhook url
    post.assert_called_once_with(ANY, json = expected_message)
    post().raise_for_status.assert_called_once()
