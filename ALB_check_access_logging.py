import boto3
import argparse


def check_access_logging_status(load_balancer_arn):
    """Check if access logging is enabled for a specific load balancer."""
    elbv2_client = boto3.client("elbv2")

    try:
        # Retrieve the current attributes for the given load balancer
        response = elbv2_client.describe_load_balancer_attributes(
            LoadBalancerArn=load_balancer_arn
        )

        # Initialize variables
        logging_enabled = False
        s3_bucket = None
        s3_prefix = None

        # Check attributes for access logging settings
        for attribute in response["Attributes"]:
            if attribute["Key"] == "access_logs.s3.enabled":
                logging_enabled = attribute["Value"] == "true"
            if attribute["Key"] == "access_logs.s3.bucket":
                s3_bucket = attribute["Value"]
            if attribute["Key"] == "access_logs.s3.prefix":
                s3_prefix = attribute["Value"]

        # Print the result
        if logging_enabled and s3_bucket:
            print(
                f"Access logging is enabled for load balancer {load_balancer_arn}. Logs are sent to bucket {s3_bucket} with prefix {s3_prefix}."
            )
        else:
            print(f"Access logging is disabled for load balancer {load_balancer_arn}.")

    except Exception as e:
        print(f"Error checking access logging status for {load_balancer_arn}: {e}")


def check_all_load_balancers():
    """Check access logging status for all load balancers."""
    elbv2_client = boto3.client("elbv2")

    try:
        # Retrieve all load balancers
        response = elbv2_client.describe_load_balancers()

        # Loop through each load balancer and check its access logging status
        for lb in response["LoadBalancers"]:
            load_balancer_arn = lb["LoadBalancerArn"]
            load_balancer_name = lb["LoadBalancerName"]

            print(f"\nChecking access logging for Load Balancer: {load_balancer_name}")
            check_access_logging_status(load_balancer_arn)

    except Exception as e:
        print(f"Error retrieving load balancers: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check access logging for one or all AWS load balancers."
    )
    parser.add_argument(
        "--load-balancer-arn",
        help="The ARN of the specific load balancer to check for access logging.",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Check all load balancers for access logging.",
    )

    args = parser.parse_args()

    if args.check_all:
        # Check all load balancers
        check_all_load_balancers()
    elif args.load_balancer_arn:
        # Check access logging status for a specific load balancer
        check_access_logging_status(args.load_balancer_arn)
    else:
        print(
            "You must either specify --load-balancer-arn to check a specific load balancer or --check-all to check all load balancers."
        )
