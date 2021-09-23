import boto3
from botocore.exceptions import ClientError


class ServerManager:
    def __init__(self, stack_name):
        self.cfn = boto3.client("cloudformation")
        self.stack = self.cfn.describe_stacks(StackName=stack_name)["Stacks"][-1]

    def stop_server(self):
        def set_state(x):
            if x.get("ParameterKey") == "ServerState":
                x["ParameterValue"] = "Stopped"
            return x

        stack_parameters = self.stack.get("Parameters")
        stack_parameters = list(map(set_state, stack_parameters))
        try:
            self.cfn.update_stack(
                StackName=self.stack.get("StackName"),
                UsePreviousTemplate=True,
                Capabilities=["CAPABILITY_IAM"],
                Parameters=stack_parameters,
            )
        except ClientError as e:
            print(e)
