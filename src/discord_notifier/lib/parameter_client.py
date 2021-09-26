import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3


class Parameter:
    def __init__(self):
        self.ssm = boto3.client("ssm")

    def set_canstart(self, value):
        e = self.ssm.put_parameter(
            Name="CanStart",
            Value=value,
            Overwrite=True,
            AllowedPattern="(True|False)",
        )
        print(e)
