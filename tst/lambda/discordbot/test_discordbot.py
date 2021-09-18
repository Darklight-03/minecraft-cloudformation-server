import pytest
from unittest.mock import patch, ANY
with patch('os.environ') as environ:
    from discordbot import lambda_handler

ping_packet = {"type": 1}
application_command_packet = {"type": 2}
component_packet = {"type": 3}
PING = 1
APP = 2
COMPONENT = 3

class incoming_packet:
    def __init__(self, type, name) -> None:
        json = {}
        json['type'] = type
        data = {}
        data['name'] = name
        json['data'] = {}
        
        self.output = {"body-json": json}

def test_ping_pong():
    assert lambda_handler.ping_pong(ping_packet) == True

def test_app_command():
    assert lambda_handler.app_command(application_command_packet) == True

def test_component():
    assert lambda_handler.component_interaction(component_packet) == True

@patch('discordbot.lambda_handler.verify_signature')
def test_blep(vsig):
    event = incoming_packet(APP, "blep").output
    lambda_handler.lambda_handler(event, "") == {"type": 5}
    vsig.assert_called_once_with(event)
