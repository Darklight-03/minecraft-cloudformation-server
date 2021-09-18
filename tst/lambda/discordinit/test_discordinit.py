import pytest
from unittest.mock import patch, ANY
with patch('os.environ') as environ:
    from discordinit import lambda_handler

@patch('requests.post')
def test_posts_commands(post):
    lambda_handler.lambda_handler("", "")
    # Assert commands are updated
    post.assert_called_with(ANY, headers=ANY, json=ANY)
    # check that header has authorization token
    assert "Authorization" in post.call_args.kwargs.get('headers').keys()
    # Check that commands is at end of url
    assert "commands" == post.call_args.args[0].split("/")[-1]