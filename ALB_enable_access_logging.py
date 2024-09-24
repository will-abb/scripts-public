import boto3
import argparse


def check_and_enable_logs(alb_arn, bucket_name):
    client = boto3.client("elbv2")
    alb_name = alb_arn.split("/")[-2]

    # Check current attributes of the ALB
    response = client.describe_load_balancer_attributes(LoadBalancerArn=alb_arn)
    attributes = response["Attributes"]

    access_logs_enabled = False
    connection_logs_enabled = False

    for attribute in attributes:
        if (
            attribute["Key"] == "access_logs.s3.enabled"
            and attribute["Value"] == "true"
        ):
            access_logs_enabled = True
        if (
            attribute["Key"] == "connection_logs.s3.enabled"
            and attribute["Value"] == "true"
        ):
            connection_logs_enabled = True

    print(f"Checking access logging for Load Balancer: {alb_name}")
    if access_logs_enabled:
        print(f"Access logging is already enabled for {alb_name}.")
    else:
        print(f"Enabling access logging for {alb_name}...")
        modify_alb_logging(client, alb_arn, bucket_name, alb_name, "access")

    print(f"Checking connection logging for Load Balancer: {alb_name}")
    if connection_logs_enabled:
        print(f"Connection logging is already enabled for {alb_name}.")
    else:
        print(f"Enabling connection logging for {alb_name}...")
        modify_alb_logging(client, alb_arn, bucket_name, alb_name, "connection")


def modify_alb_logging(client, alb_arn, bucket_name, alb_name, log_type):
    if log_type == "access":
        attributes = [
            {"Key": "access_logs.s3.enabled", "Value": "true"},
            {"Key": "access_logs.s3.bucket", "Value": bucket_name},
            {"Key": "access_logs.s3.prefix", "Value": alb_name},
        ]
    elif log_type == "connection":
        attributes = [
            {"Key": "connection_logs.s3.enabled", "Value": "true"},
            {"Key": "connection_logs.s3.bucket", "Value": bucket_name},
            {"Key": "connection_logs.s3.prefix", "Value": alb_name},
        ]
    try:
        response = client.modify_load_balancer_attributes(
            LoadBalancerArn=alb_arn, Attributes=attributes
        )
        print(f"{log_type.capitalize()} logging enabled successfully for {alb_name}.")
    except Exception as e:
        print(f"Error enabling {log_type} logging for {alb_name}:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enable access and connection logs for an Application Load Balancer (ALB)."
    )
    parser.add_argument(
        "--alb-arn", required=True, help="ARN of the Application Load Balancer."
    )
    parser.add_argument(
        "--s3-bucket", required=True, help="S3 Bucket name where logs will be stored."
    )

    args = parser.parse_args()

    check_and_enable_logs(args.alb_arn, args.s3_bucket)
