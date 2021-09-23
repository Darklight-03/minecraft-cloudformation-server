from discord_bot.lib.server_menu import ServerState
from datetime import datetime


class newDescribeStacks:
    def __init__(
        self,
        stack_name="stack_name",
        stack_id="stack_id",
        stack_status="UPDATE_COMPLETE",
        parameters=["p1", "p2", "p3", "ServerState", "p4", "p5"],
        server_state=ServerState.STOPPED,
    ):
        parameters = [{"ParameterKey": v, "ParameterValue": v} for v in parameters]

        def set_state(param):
            if param.get("ParameterKey") == "ServerState":
                param["ParameterValue"] = server_state
                return param
            return param

        self.parameters = list(map(set_state, parameters))
        self.stack_name = stack_name
        self.server_state = server_state
        self.stack_id = stack_id
        self.stack_status = stack_status

        self.output = {
            "Stacks": [
                {
                    "StackName": self.stack_name,
                    "StackId": self.stack_id,
                    "StackStatus": self.stack_status,
                    "Parameters": self.parameters,
                    "ChangeSetId": "string",
                    "Description": "string",
                    "CreationTime": datetime(2015, 1, 1),
                    "DeletionTime": datetime(2015, 1, 1),
                    "LastUpdatedTime": datetime(2015, 1, 1),
                    "Capabilities": [
                        "CAPABILITY_IAM",
                    ],
                }
            ]
        }
