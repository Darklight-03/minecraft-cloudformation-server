import boto3


def provide_cfn_client():
    return boto3.client("cloudformation")


def provide_ssm_client():
    return boto3.client("ssm")
