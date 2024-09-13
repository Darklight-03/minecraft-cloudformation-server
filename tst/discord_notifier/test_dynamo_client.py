import warnings
from datetime import datetime
from unittest.mock import patch

from discord_notifier.tstlib.test_mock_objects import STACK_NAME, TABLE_NAME

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import boto3

from botocore.stub import Stubber
from pytest import fixture

from discord_notifier.lib.dynamo_client import Dynamo

INSTANCE_ID = "i-00000"
PUBLIC_DNS_NAME = "test.com"
INSTANCE_STATE = "running"
INSTANCE_STOPPED_STATE = "stopped"
INSTANCE_LAUNCH_MSG = "EC2 Instance Launch Successful"
INSTANCE_STOP_MSG = "EC2 Instance Terminate Successful"
DESCRIBE_EC2 = {
    "Reservations": [
        {
            "Instances": [
                {
                    "InstanceId": INSTANCE_ID,
                    "InstanceType": "t1.micro",
                    "LaunchTime": datetime(2015, 1, 1),
                    "PublicDnsName": PUBLIC_DNS_NAME,
                    "PublicIpAddress": "string",
                    "State": {
                        "Code": 123,
                        "Name": "running",
                    },
                },
            ],
        },
    ],
}


@fixture
def dynamo_client():
    dynamo = boto3.client("dynamodb", region_name="us-west-2")
    stubber = Stubber(dynamo)
    stubber.activate()
    with patch("boto3.client") as mock_boto3:
        mock_boto3.return_value = dynamo
        yield stubber
        stubber.assert_no_pending_responses()


@fixture
def ec2_resource():
    ec2 = boto3.resource("ec2", region_name="us-west-2")
    stubber = Stubber(ec2.meta.client)
    stubber.activate()
    with patch("boto3.resource") as mock_boto3:
        mock_boto3.return_value = ec2
        response = DESCRIBE_EC2
        expected_params = {"InstanceIds": [INSTANCE_ID]}
        stubber.add_response("describe_instances", response, expected_params)
        yield stubber
        stubber.assert_no_pending_responses()


def test_get_dns(ec2_resource):
    assert Dynamo().get_dns(INSTANCE_ID) == PUBLIC_DNS_NAME


def test_put_start_instance_status(dynamo_client, ec2_resource):
    response = {}
    expected_params = {
        "ExpressionAttributeNames": {"#attrib": "InstanceDns"},
        "ExpressionAttributeValues": {":val": {"S": PUBLIC_DNS_NAME}},
        "Key": {"StackName": {"S": STACK_NAME}},
        "TableName": TABLE_NAME,
        "UpdateExpression": "SET #attrib = :val",
    }
    dynamo_client.add_response("update_item", response, expected_params)

    expected_params = {
        "ExpressionAttributeNames": {"#attrib": "InstanceStatus"},
        "ExpressionAttributeValues": {":val": {"S": INSTANCE_STATE}},
        "Key": {"StackName": {"S": STACK_NAME}},
        "TableName": TABLE_NAME,
        "UpdateExpression": "SET #attrib = :val",
    }
    dynamo_client.add_response("update_item", response, expected_params)
    Dynamo().put_instance_status(
        {
            "detail-type": INSTANCE_LAUNCH_MSG,
            "detail": {"state": INSTANCE_STATE, "EC2InstanceId": INSTANCE_ID},
        }
    )


def test_put_stop_instance_status(dynamo_client):
    response = {}
    expected_params = {
        "ExpressionAttributeNames": {"#attrib": "InstanceStatus"},
        "ExpressionAttributeValues": {":val": {"S": INSTANCE_STOPPED_STATE}},
        "Key": {"StackName": {"S": STACK_NAME}},
        "TableName": TABLE_NAME,
        "UpdateExpression": "SET #attrib = :val",
    }
    dynamo_client.add_response("update_item", response, expected_params)
    Dynamo().put_instance_status(
        {
            "detail-type": INSTANCE_STOP_MSG,
            "detail": {"state": INSTANCE_STOPPED_STATE, "EC2InstanceId": INSTANCE_ID},
        }
    )


def test_put_ecs_status(dynamo_client):
    ECS_STATUS = "testStatus"
    response = {}
    expected_params = {
        "ExpressionAttributeNames": {"#attrib": "EcsStatus"},
        "ExpressionAttributeValues": {":val": {"S": ECS_STATUS}},
        "Key": {"StackName": {"S": STACK_NAME}},
        "TableName": TABLE_NAME,
        "UpdateExpression": "SET #attrib = :val",
    }
    dynamo_client.add_response("update_item", response, expected_params)
    Dynamo().put_ecs_status(ECS_STATUS)
