import os
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3


class Dynamo:
    def __init__(self):
        self.dynamo = boto3.client("dynamodb")
        self.ec2 = boto3.resource("ec2")
        self.stack_name = os.environ["STACK_NAME"]
        self.table_name = os.environ["TABLE_NAME"]

    def get_key(self):
        return {"StackName": {"S": self.stack_name}}

    def get_dns(self, instance_id):
        instance = self.ec2.Instance(instance_id)
        return instance.public_dns_name

    def update_item(self, attrib, val):
        self.dynamo.update_item(
            TableName=self.table_name,
            Key=self.get_key(),
            UpdateExpression="SET #attrib = :val",
            ExpressionAttributeValues={":val": {"S": val}},
            ExpressionAttributeNames={"#attrib": attrib},
        )

    def put_ecs_status(self, ecs_status):
        self.update_item("EcsStatus", ecs_status)

    def put_instance_status(self, detail):
        if detail["state"] == "running":
            # get dns name with ec2 api
            self.update_item("InstanceDns", self.get_dns(detail["instance-id"]))
        self.update_item("InstanceStatus", detail["state"])
