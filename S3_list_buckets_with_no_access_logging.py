import boto3
import argparse
from botocore.exceptions import ClientError


def get_s3_client():
    """Create an S3 client using boto3."""
    return boto3.client("s3")


def get_buckets_with_tag(s3_client, tag_key, tag_value):
    """Retrieve buckets that have a specific tag."""
    tagged_buckets = []
    all_buckets = s3_client.list_buckets()

    for bucket in all_buckets["Buckets"]:
        bucket_name = bucket["Name"]
        try:
            tags = s3_client.get_bucket_tagging(Bucket=bucket_name)
            for tag in tags["TagSet"]:
                if tag["Key"] == tag_key and tag["Value"] == tag_value:
                    tagged_buckets.append(bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchTagSet":
                continue  # Skip buckets without tags
            else:
                print(f"Client error occurred: {e}")

    return tagged_buckets


def check_buckets_logging(s3_client, buckets):
    """Check and list the S3 buckets without logging enabled."""
    buckets_without_logging = []
    for bucket_name in buckets:
        try:
            logging = s3_client.get_bucket_logging(Bucket=bucket_name)
            if "LoggingEnabled" not in logging:
                buckets_without_logging.append(bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "AccessDenied":
                print(f"Access denied to get logging info for bucket: {bucket_name}")
            else:
                print(
                    f"Client error occurred while accessing bucket {bucket_name}: {e}"
                )
    return buckets_without_logging


def main():
    parser = argparse.ArgumentParser(
        description="Check which S3 buckets do not have logging enabled."
    )
    parser.add_argument(
        "--tag",
        type=str,
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Tag key and value to filter buckets.",
    )
    args = parser.parse_args()

    s3_client = get_s3_client()
    if args.tag:
        tag_key, tag_value = args.tag
        buckets = get_buckets_with_tag(s3_client, tag_key, tag_value)
    else:
        buckets_response = s3_client.list_buckets()
        buckets = [bucket["Name"] for bucket in buckets_response["Buckets"]]

    total_buckets = len(buckets)
    buckets_without_logging = check_buckets_logging(s3_client, buckets)
    num_buckets_without_logging = len(buckets_without_logging)

    if num_buckets_without_logging > 0:
        print(
            f"Logging is not enabled for the following {num_buckets_without_logging} out of {total_buckets} buckets:"
        )
        print("\n".join(buckets_without_logging))
    else:
        print(
            f"Logging is enabled for all {total_buckets} checked buckets or access was denied."
        )


if __name__ == "__main__":
    main()
