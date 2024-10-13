import os

from pytest import fixture

import discord_notifier.tstlib.test_mock_objects as test_constants


@fixture(autouse=True)
def environs():
    os.environ["WebhookUrl"] = "WebhookUrl"
    os.environ["STACK_NAME"] = test_constants.STACK_NAME
    os.environ["TABLE_NAME"] = test_constants.TABLE_NAME
    os.environ["AWS_REGION"] = "us-west-2"


@fixture()
def ec2_instance_statechange_event():
    return {
        "id": "7bf73129-1428-4cd3-a780-95db273d1602",
        "detail-type": "EC2 Instance State-change Notification",
        "source": "aws.ec2",
        "account": "123456789012",
        "time": "2021-11-11T21:29:54Z",
        "region": "us-east-1",
        "resources": ["arn:aws:ec2:us-east-1:123456789012:instance/i-abcd1111"],
        "detail": {"instance-id": "i-abcd1111", "state": "pending"},
    }


@fixture
def ecs_statechange_event():
    return {
        "version": "0",
        "id": "af3c496d-f4a8-65d1-70f4-a69d52e9b584",
        "detail-type": "ECS Service Action",
        "source": "aws.ecs",
        "account": "111122223333",
        "time": "2019-11-19T19:27:22Z",
        "region": "us-west-2",
        "resources": ["arn:aws:ecs:us-west-2:111122223333:service/default/servicetest"],
        "detail": {
            "eventType": "INFO",
            "eventName": "SERVICE_STEADY_STATE",
            "clusterArn": "arn:aws:ecs:us-west-2:111122223333:cluster/default",
            "createdAt": "2019-11-19T19:27:22.695Z",
        },
    }


@fixture
def asg_statechange_event():
    return {
        "version": "0",
        "id": "12345678-1234-1234-1234-123456789012",
        "detail-type": "EC2 Instance Launch Successful",
        "source": "aws.autoscaling",
        "account": "123456789012",
        "time": "yyyy-mm-ddThh:mm:ssZ",
        "region": "us-west-2",
        "resources": ["auto-scaling-group-arn", "instance-arn"],
        "detail": {
            "StatusCode": "InProgress",
            "Description": "Launching a new EC2 instance: i-12345678",
            "AutoScalingGroupName": "my-asg",
            "ActivityId": "87654321-4321-4321-4321-210987654321",
            "Details": {
                "Availability Zone": "us-west-2b",
                "Subnet ID": "subnet-12345678",
            },
            "RequestId": "12345678-1234-1234-1234-123456789012",
            "StatusMessage": "",
            "EndTime": "yyyy-mm-ddThh:mm:ssZ",
            "EC2InstanceId": "i-1234567890abcdef0",
            "StartTime": "yyyy-mm-ddThh:mm:ssZ",
            "Cause": "description-text",
            "Origin": "EC2",
            "Destination": "AutoScalingGroup",
        },
    }
