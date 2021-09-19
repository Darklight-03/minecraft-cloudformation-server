# request types we can receive
class RequestType:
    MESSAGE_PING = 1
    MESSAGE_APP = 2
    MESSAGE_COMPONENT = 3


# check request types
def is_ping(body):
    return body.get("type") == RequestType.MESSAGE_PING


def is_app_command(body):
    return body.get("type") == RequestType.MESSAGE_APP


def is_component_interaction(body):
    return body.get("type") == RequestType.MESSAGE_COMPONENT


def is_blep(body):
    return body.get("data").get("name") == "blep"
