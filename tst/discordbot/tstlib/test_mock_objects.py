from lib.server_menu import ServerState


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

        parameters = list(map(set_state, parameters))

        self.output = {
            "Stacks": [
                {
                    "StackName": stack_name,
                    "StackId": stack_id,
                    "StackStatus": stack_status,
                    "Parameters": parameters,
                }
            ]
        }
