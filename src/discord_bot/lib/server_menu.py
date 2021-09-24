import os
import warnings
from datetime import datetime

from botocore.exceptions import ClientError
from discord_bot.lib.components import Button, ButtonStyle
from discord_bot.lib.request import Components
from discord_bot.lib.response import (
    Embed,
    EmbedColor,
    Response,
    ResponseType,
)

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
        self.can_start = (
            ssm.get_parameter(Name="CanStart").get("Parameter").get("Value") == "True"
        )
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
        self.response.with_disabled_start().with_disabled_stop()
        self.response.with_title(
            f"Server is currently {ServerState.verb(self.desired_state)}..."
        )
        return self.response.get_response()

    def get_error(self):
        if "is in UPDATE_IN_PROGRESS state" in self.output:
            self.output = "Server is still loading, please wait for it to start/stop."
            return (
                self.response.with_disabled_start()
                .with_disabled_stop()
                .with_title(self.output)
                .get_response()
            )
        elif "No updates are to be performed" in self.output:
            self.output = f"Server is already in state {self.desired_state}."
            if self.desired_state == ServerState.RUNNING:
                return (
                    self.response.with_disabled_start()
                    .with_title(self.output)
                    .get_response()
                )
            else:
                return (
                    self.response.with_disabled_stop()
                    .with_title(self.output)
                    .get_response()
                )
        else:
            # disable both buttons for unknown errors
            return (
                self.response.with_disabled_start()
                .with_disabled_stop()
                .with_title(self.output)
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
        self.update_stack_status()
        self.update_can_start()
        self.init_menu(type)
        self.fetch_menu_update()

    # Updates the current status of the stack
    def update_stack_status(self):
        cfn = boto3.client("cloudformation")
        stack = cfn.describe_stacks(StackName=os.environ.get("STACK_NAME")).get(
            "Stacks"
        )[-1]

        self.current_state = [
            parameter.get("ParameterValue")
            for parameter in stack.get("Parameters")
            if parameter.get("ParameterKey") == "ServerState"
        ][0]
        self.stack_status = stack.get("StackStatus")

    # gets the CanStart variable
    def update_can_start(self):
        ssm = boto3.client("ssm")
        self.can_start = (
            ssm.get_parameter(Name="CanStart").get("Parameter").get("Value") == "True"
        )

    # Buttons
    def with_disabled_start(self):
        self.response.component_rows[0].get_component(
            "button_start_server"
        ).disabled = True
        return self

    def with_disabled_stop(self):
        self.response.component_rows[0].get_component(
            "button_stop_server"
        ).disabled = True
        return self

    # Setup initial menu
    def init_menu(self, type):
        self.response = Response(type)
        self.menu = Embed().with_title(
            f"Server is currently {self.current_state.lower()}"
        )
        self.response.add_embed(self.menu)
        self.response.add_component_row()
        self.response.component_rows[0].add_component(
            Button(ButtonStyle.SUCCESS, label="Start", custom_id="button_start_server")
        )
        self.response.component_rows[0].add_component(
            Button(ButtonStyle.DANGER, label="Stop", custom_id="button_stop_server")
        )
        self.response.component_rows[0].add_component(
            Button(
                ButtonStyle.SECONDARY,
                label="Refresh",
                custom_id="button_refresh_menu",
            )
        )

    # Update menu with new information
    def fetch_menu_update(self):
        if self.current_state == ServerState.RUNNING:
            self.with_disabled_start()
        if self.current_state == ServerState.STOPPED:
            self.with_disabled_stop()
        if self.stack_status not in [
            "UPDATE_COMPLETE",
            "CREATE_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE",
        ]:
            self.with_disabled_start().with_disabled_stop()
            self.with_title(
                f"Server is currently {ServerState.verb(self.current_state)}..."
            )
        elif not self.can_start:
            self.with_disabled_start()
        self.add_embeds()

    # Menu assignments
    def with_title(self, title):
        self.menu.with_title(title)
        return self

    def set_embed_data(self, description, color):
        self.menu.with_description(description)
        self.menu.with_color(color)

    # extra response data
    def add_embed(self, embed):
        self.response.add_embed(embed)
        return self

    def add_embeds(self):
        if self.can_start:
            self.set_embed_data(
                "it will be available until " f"{self.get_next_stop_time()}",
                EmbedColor.GREEN,
            )
        else:
            self.set_embed_data(
                "it will next be available to start at "
                f"{self.get_next_start_time()}",
                EmbedColor.RED,
            )

    def get_next_start_time(self):
        return f"(not yet implemented {datetime.now()})"

    def get_next_stop_time(self):
        return f"(not yet implemented {datetime.now()})"

    def get_response(self):
        return self.response.get_response()

    def run(self):
        return self.response.get_response()
