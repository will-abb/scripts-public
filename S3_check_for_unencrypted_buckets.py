import boto3


def list_unencrypted_s3_buckets():
    """
    List all S3 buckets that do not have default encryption enabled.
    """
    s3_client = boto3.client("s3")

    buckets = s3_client.list_buckets()["Buckets"]

    unencrypted_buckets = []
    for bucket in buckets:
        bucket_name = bucket["Name"]
        try:
            # If the bucket has default encryption enabled, an exception will not be thrown
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
        except s3_client.exceptions.ClientError as e:
            if (
                e.response["Error"]["Code"]
                == "ServerSideEncryptionConfigurationNotFoundError"
            ):
                unencrypted_buckets.append(bucket_name)
            elif e.response["Error"]["Code"] == "AccessDenied":
                print(
                    f"Access Denied for bucket: {bucket_name}. Moving on to the next bucket."
                )
            else:
                print(f"Unhandled error for bucket {bucket_name}: {e}")
                print("Continuing with the next bucket.")

    return unencrypted_buckets


def main():
    """
    The main function that prints out all unencrypted S3 bucket names.
    """
    unencrypted_buckets = list_unencrypted_s3_buckets()
    if unencrypted_buckets:
        print("Unencrypted S3 Buckets:")
        for bucket in unencrypted_buckets:
            print(bucket)
    else:
        print("All S3 buckets have encryption enabled or access was denied.")


if __name__ == "__main__":
    main()
