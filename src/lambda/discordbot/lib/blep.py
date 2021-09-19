import os
import warnings

from lib.components import Button, ButtonStyle
from lib.request import Components
from lib.response import MessageResponse, ResponseType

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3


class ServerState:
    def __init__(self, request):
        class ServerState:
            RUNNING = "Running"
            STOPPED = "Stopped"

        self.request = request
        component = self.request.get_component()
        if component == Components.START_SERVER:
            self.desired_state = ServerState.RUNNING
            self.response_message = "Starting Server..."
        if component == Components.STOP_SERVER:
            self.desired_state = ServerState.STOPPED
            self.response_message = "Stopping Server..."
        self.stack_name = os.environ.get("STACK_NAME")
        self.cfn = boto3.client("cloudformation")
        self.stack = self.cfn.describe_stacks(StackName=self.stack_name)

    # may want to do this in new lambda function if take too long (probably)
    def start_server(self):
        def set_state(x):
            if x.get("ParameterKey") == "ServerState":
                x["ParameterValue"] = self.desired_state
            return x

        stack_parameters = self.stack.get("Stacks")[-1].get("Parameters")
        stack_parameters = list(map(set_state, stack_parameters))
        self.cfn.update_stack(
            StackName=self.stack_name,
            UsePreviousTemplate=True,
            Capabilities=["CAPABILITY_IAM"],
            Parameters=stack_parameters,
        )
        return True

    def get_message_update_success(self):
        response = MessageResponse(
            ResponseType.COMPONENT_MESSAGE, self.response_message
        )
        response.add_components_from_request(self.request.message.get("components"))
        return response.get_response()

    def run(self):
        if self.start_server():
            return self.get_message_update_success()


class ServerMenu:
    def __init__(self, request):
        self.request = request
        self.menu = MessageResponse(ResponseType.MESSAGE, "Test Message")
        self.menu.add_component_row()
        self.menu.component_rows[0].add_component(
            Button(ButtonStyle.SUCCESS, label="Start", id="button_start_server")
        )
        self.menu.component_rows[0].add_component(
            Button(
                ButtonStyle.DANGER, label="Stop", id="button_stop_server", disabled=True
            )
        )
        self.menu.component_rows[0].add_component(
            Button(ButtonStyle.SECONDARY, label="Refresh", id="button_refresh_menu")
        )

    def run(self):
        return self.menu.get_response()
