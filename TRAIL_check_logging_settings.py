import boto3
from botocore.exceptions import ClientError


def get_cloudtrail_info():
    """Retrieve CloudTrail configuration and associated S3 bucket details."""
    cloudtrail_client = boto3.client("cloudtrail")
    s3_client = boto3.client("s3")

    try:
        trails = cloudtrail_client.describe_trails(includeShadowTrails=True)
        if not trails["trailList"]:
            print("No CloudTrail trails available in this account.")
            return []
    except ClientError as e:
        print(f"Error retrieving trails: {e}")
        return []

    trail_details = []

    for trail in trails["trailList"]:
        details = {
            "Name": trail["Name"],
            "S3BucketName": trail.get("S3BucketName", "No S3 bucket specified"),
            "LogFileValidationEnabled": trail.get("LogFileValidationEnabled", False),
            "IsMultiRegionTrail": trail.get("IsMultiRegionTrail", False),
            "LifecycleRules": "No lifecycle policy.",
            "AccessDeniedError": "",
        }

        if "S3BucketName" in trail:
            try:
                lifecycle = s3_client.get_bucket_lifecycle_configuration(
                    Bucket=trail["S3BucketName"]
                )
                rules = lifecycle.get("Rules", [])
                if rules:
                    details["LifecycleRules"] = [
                        {
                            "ID": rule["ID"],
                            "Status": rule["Status"],
                            "Expiration": rule.get("Expiration", {}),
                        }
                        for rule in rules
                    ]
            except ClientError as e:
                if e.response["Error"]["Code"] == "AccessDenied":
                    details[
                        "AccessDeniedError"
                    ] = "Access Denied for Lifecycle Configurations."
                elif e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
                    details["LifecycleRules"] = "No lifecycle policy."
                else:
                    print(f"Error accessing S3 Bucket {trail['S3BucketName']}: {e}")

        trail_details.append(details)

    return trail_details


def main():
    trail_info = get_cloudtrail_info()
    if trail_info:
        for info in trail_info:
            print(f"Trail Name: {info['Name']}")
            print(f"S3 Bucket Name: {info['S3BucketName']}")
            print(f"Log File Validation Enabled: {info['LogFileValidationEnabled']}")
            print(f"Is Multi-Region Trail: {info['IsMultiRegionTrail']}")
            print(f"Lifecycle Rules: {info['LifecycleRules']}")
            if info["AccessDeniedError"]:
                print(info["AccessDeniedError"])
            print("-" * 60)


if __name__ == "__main__":
    main()
