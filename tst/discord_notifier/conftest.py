import os

from pytest import fixture

STACK_NAME = "StackName"
TABLE_NAME = "TableName"
WEBHOOK_URL = "WebhookUrl"


@fixture(autouse=True)
def environs():
    os.environ["WebhookUrl"] = "WebhookUrl"
    os.environ["STACK_NAME"] = "StackName"
    os.environ["TABLE_NAME"] = "TableName"
