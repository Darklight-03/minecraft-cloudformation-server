import os
import warnings

from datetime import datetime

from botocore.exceptions import ClientError
from lib.components import Button, ButtonStyle
from lib.request import Components
from lib.response import MessageResponse, ResponseType

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3


class ServerState:
    RUNNING = "Running"
    STOPPED = "Stopped"


class SetServerState:
    def __init__(self, request):

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
        self.response = ServerMenu(ResponseType.COMPONENT_MESSAGE)

        def set_state(x):
            if x.get("ParameterKey") == "ServerState":
                x["ParameterValue"] = self.desired_state
            return x

        stack_parameters = self.stack.get("Stacks")[-1].get("Parameters")
        stack_parameters = list(map(set_state, stack_parameters))
        try:
            self.cfn.update_stack(
                StackName=self.stack_name,
                UsePreviousTemplate=True,
                Capabilities=["CAPABILITY_IAM"],
                Parameters=stack_parameters,
            )
        except ClientError as e:
            return str(e)
        return "Success"

    def get_message_update_success(self):
        return (
            self.response.withDisabledStart()
            .withDisabledStop()
            .withContent(
                f"Server is currently changing to {self.desired_state} status..."
            )
            .run()
        )

    def get_validation_error(self):
        if "is in UPDATE_IN_PROGRESS state" in self.output:
            self.output = "Server is still loading, please wait for it to start/stop."
        elif "No updates are to be performed" in self.output:
            self.output = f"Server is already in state {self.desired_state}."
        if self.desired_state == ServerState.RUNNING:
            return self.response.withDisabledStart().withContent(self.output).run()
        else:
            return self.response.withDisabledStop().withContent(self.output).run()

    def run(self):
        self.output = self.start_server()
        if self.output == "Success":
            return self.get_message_update_success()
        elif "ValidationError" in self.output:
            return self.get_validation_error()


class ServerMenu:
    def __init__(self, type):
        self.menu = MessageResponse(type, f"Test Message {str(datetime.now())}")
        self.menu.add_component_row()
        self.menu.component_rows[0].add_component(
            Button(ButtonStyle.SUCCESS, label="Start", id="button_start_server")
        )
        self.menu.component_rows[0].add_component(
            Button(ButtonStyle.DANGER, label="Stop", id="button_stop_server")
        )
        self.menu.component_rows[0].add_component(
            Button(
                ButtonStyle.SECONDARY,
                label="Refresh",
                id="button_refresh_menu",
                disabled=False,
            )
        )

    def withDisabledStart(self):
        self.menu.component_rows[0].get_component("button_start_server").disabled = True
        return self

    def withDisabledStop(self):
        self.menu.component_rows[0].get_component("button_stop_server").disabled = True
        return self

    def withContent(self, content):
        self.menu.content = content
        return self

    def run(self):
        return self.menu.get_response()
