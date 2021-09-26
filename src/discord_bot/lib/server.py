import os

from botocore.exceptions import ClientError
from discord_bot.lib.components import Components
from discord_bot.lib.provider import provide_cfn_client, provide_ssm_client


class ServerState:
    RUNNING = "Running"
    STOPPED = "Stopped"

    def verb(state):
        return "starting" if state == ServerState.RUNNING else "stopping"

    def get_state_from_component(component):
        if component == Components.START_SERVER:
            return ServerState.RUNNING
        elif component == Components.STOP_SERVER:
            return ServerState.STOPPED
        else:
            return None


class Server:
    def __init__(self):
        self.cfn = provide_cfn_client()
        self.stack_name = os.environ.get("STACK_NAME")
        self.ssm = provide_ssm_client()
        self.current_state = "Unknown"
        self.stack_status = "Unknown"
        self.updated = False

    def update(self):
        # update ssm variable
        self.updated = True
        self.can_start = (
            self.ssm.get_parameter(Name="CanStart").get("Parameter").get("Value")
            == "True"
        )
        # update stack status
        self.stack = self.cfn.describe_stacks(StackName=self.stack_name)
        self.stack_parameters = self.stack.get("Stacks")[0].get("Parameters")

        self.current_state = next(
            (x for x in self.stack_parameters if x["ParameterKey"] == "ServerState")
        )["ParameterValue"]
        self.stack_status = self.stack.get("Stacks")[0].get("StackStatus")

    def set_state(self, state: str):
        if state == ServerState.RUNNING and self.can_start is False:
            return Exception("Server cannot be started outside the time window")
        if self.current_state == state and self.stack_status in [
            "UPDATE_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE",
            "CREATE_COMPLETE",
        ]:
            return Exception(f"Server is already {state.lower()}")

        for parameter in self.stack_parameters:
            if parameter["ParameterKey"] == "ServerState":
                parameter["ParameterValue"] = state
        try:
            self.cfn.update_stack(
                StackName=self.stack_name,
                UsePreviousTemplate=True,
                Capabilities=["CAPABILITY_IAM"],
                Parameters=self.stack_parameters,
            )
            self.stack_status = "UPDATE_IN_PROGRESS"
        except ClientError as e:
            return e
        return f"Server is currently {ServerState.verb(state)}"
