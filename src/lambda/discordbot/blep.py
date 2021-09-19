import warnings

from discordbot.components import Button, ButtonStyle
from discordbot.response import ChannelMessageResponse

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3


# may want to do this in new lambda function if take too long (probably)
def start_server():
    cfn = boto3.client("cloudformation")
    stack = cfn.describe_stacks(StackName="${AWS::StackName}")
    parameters = stack.get("Stacks")[-1].get("Parameters")

    def set_state(x):
        if x.get("ParameterKey") == "ServerState":
            x["ParameterValue"] = "Started"
        return x

    parameters = list(map(set_state, parameters))
    cfn.update_stack(
        StackName="${AWS::StackName}",
        UsePreviousTemplate=True,
        Capabilities=["CAPABILITY_IAM"],
        Parameters=parameters,
    )


def get_response():
    BLEP = ChannelMessageResponse("Test Message")
    BLEP.add_component_row()
    BLEP.component_rows[0].add_component(
        Button(ButtonStyle.PRIMARY, label="Yes", id="yesbutton")
    )
    BLEP.component_rows[0].add_component(
        Button(ButtonStyle.DANGER, label="No", id="nobutton")
    )
    return BLEP.get_response()


def blep(body):
    return get_response()
