from datetime import datetime

from discord_bot.lib.server_menu import ServerState

INSTANCE_DNS = "ec2.us-west-2.compute.amazonaws.com"
STACK_NAME = "STACK_NAME"
STACK_ID = f"arn:aws:cloudformation:us-west-2:000000000000:stack\n\
/{STACK_NAME}/00000000-0000-0000-0000-000000000000"
TABLE_NAME = "STACK_NAME-StatusTable-AAAAAAA"


class newDescribeStacks:
    def __init__(
        self,
        stack_name=STACK_NAME,
        stack_id=STACK_ID,
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


class newGetItem:
    def __init__(
        self,
        ecs_status="SERVICE_STEADY_STATE",
        instance_dns=INSTANCE_DNS,
        stack_name=STACK_NAME,
        instance_status="terminated",
    ):

        self.output = {
            "Item": {
                "EcsStatus": {"S": ecs_status},
                "InstanceDns": {"S": instance_dns},
                "StackName": {"S": stack_name},
                "InstanceStatus": {"S": instance_status},
            }
        }
