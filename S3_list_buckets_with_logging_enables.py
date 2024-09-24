import boto3
import argparse


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
        except s3_client.exceptions.NoSuchTagSet:
            continue  # Skip buckets without tags

    return tagged_buckets


def check_buckets_with_logging(s3_client, buckets):
    """Check and list the S3 buckets with logging enabled."""
    buckets_with_logging = []
    for bucket_name in buckets:
        try:
            logging = s3_client.get_bucket_logging(Bucket=bucket_name)
            if "LoggingEnabled" in logging:  # Corrected this line
                buckets_with_logging.append(bucket_name)
        except boto3.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "AccessDenied":
                print(f"Access denied to get logging info for bucket: {bucket_name}")
            else:
                print(f"Error accessing bucket {bucket_name}: {e}")
    return buckets_with_logging


def main():
    parser = argparse.ArgumentParser(
        description="List S3 buckets that have logging enabled."
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
        buckets = [bucket["Name"] for bucket in s3_client.list_buckets()["Buckets"]]

    buckets_with_logging = check_buckets_with_logging(s3_client, buckets)
    num_buckets = len(buckets_with_logging)
    if num_buckets > 0:
        print(f"Logging is enabled for the following {num_buckets} buckets:")
        for bucket in buckets_with_logging:
            print(bucket)
    else:
        print("No buckets with logging enabled were found or access was denied.")


if __name__ == "__main__":
    main()
