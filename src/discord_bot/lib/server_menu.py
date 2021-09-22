import os
import warnings

from datetime import datetime

from botocore.exceptions import ClientError
from discord_bot.lib.components import Button, ButtonStyle
from discord_bot.lib.request import Components
from discord_bot.lib.response import MessageResponse, ResponseType

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3


class ServerState:
    RUNNING = "Running"
    STOPPED = "Stopped"

    def verb(state):
        return "starting" if state == ServerState.RUNNING else "stopping"

    def get_state_from_component(component):
        return (
            ServerState.RUNNING
            if component == Components.START_SERVER
            else ServerState.STOPPED
        )


class SetServerState:
    def __init__(self, request):
        self.request = request
        component = self.request.get_component()
        self.desired_state = ServerState.get_state_from_component(component)
        self.stack_name = os.environ.get("STACK_NAME")
        self.cfn = boto3.client("cloudformation")
        ssm = boto3.client("ssm")
        self.can_start = ssm.get_parameter(Name="CanStart") == "True"
        self.response = ServerMenu(ResponseType.COMPONENT_MESSAGE)

    # may want to do this in new lambda function if take too long (probably)
    def start_server(self):
        if self.desired_state == ServerState.RUNNING and not self.can_start:
            # TODO return this in an embed with more detail
            # (next time it can be started for example)
            return (
                "Server cannot currently be started"
                " as it is not within the time window."
            )
        stack = self.cfn.describe_stacks(StackName=self.stack_name)

        def set_state(x):
            if x.get("ParameterKey") == "ServerState":
                x["ParameterValue"] = self.desired_state
            return x

        stack_parameters = stack.get("Stacks")[-1].get("Parameters")
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
        self.response.withDisabledStart().withDisabledStop()
        self.response.withContent(
            f"Server is currently {ServerState.verb(self.desired_state)}..."
        )
        return self.response.get_response()

    def get_error(self):
        if "is in UPDATE_IN_PROGRESS state" in self.output:
            self.output = "Server is still loading, please wait for it to start/stop."
            return (
                self.response.withDisabledStart()
                .withDisabledStop()
                .withContent(self.output)
                .get_response()
            )
        elif "No updates are to be performed" in self.output:
            self.output = f"Server is already in state {self.desired_state}."
            if self.desired_state == ServerState.RUNNING:
                return (
                    self.response.withDisabledStart()
                    .withContent(self.output)
                    .get_response()
                )
            else:
                return (
                    self.response.withDisabledStop()
                    .withContent(self.output)
                    .get_response()
                )
        else:
            # disable both buttons for unknown errors
            return (
                self.response.withDisabledStart()
                .withDisabledStop()
                .withContent(self.output)
                .get_response()
            )

    def run(self):
        self.output = self.start_server()
        if self.output == "Success":
            return self.get_message_update_success()
        elif "ValidationError" in self.output:
            return self.get_error()
        else:
            # for now use validationerror for any error
            return self.get_error()


class ServerMenu:
    def __init__(self, type):
        self.cfn = boto3.client("cloudformation")
        self.stack = self.cfn.describe_stacks(
            StackName=os.environ.get("STACK_NAME")
        ).get("Stacks")[-1]
        self.current_state = [
            parameter.get("ParameterValue")
            for parameter in self.stack.get("Parameters")
            if parameter.get("ParameterKey") == "ServerState"
        ][0]
        self.stack_status = self.stack.get("StackStatus")
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

    def get_response(self):
        return self.menu.get_response()

    def run(self):
        if self.stack_status not in [
            "UPDATE_COMPLETE",
            "CREATE_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE",
        ]:
            self.withDisabledStart().withDisabledStop()
            self.withContent(
                f"Server is currently {ServerState.verb(self.current_state)}..."
            )
        else:
            if self.current_state == ServerState.RUNNING:
                self.withDisabledStart()
            elif self.current_state == ServerState.STOPPED:
                self.withDisabledStop()
            self.withContent(f"Server is currently {self.current_state.lower()}")
        return self.menu.get_response()
