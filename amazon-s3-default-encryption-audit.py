import boto3
import sys
import os
import time
import csv
from contextlib import suppress

# Hard-coded output location for the report.
bucketEncryptionReportLocation = "/home/wil031583/Documents/"
bucketEncryptionReport = (
    bucketEncryptionReportLocation
    + "bucketEncryptionReport_"
    + time.strftime("%Y%m%d-%H%M%S")
    + ".csv"
)

# Define the AWS Regions to check.
regions = ["us-east-1", "us-west-2"]

# Create empty output file to store report.
open(bucketEncryptionReport, "a").close()

# Create function to add headers into the CSV file.
def appendHeaders():
    headers = [
        "Bucket Name",
        "Default Encryption Mode",
        "SSE-KMS Key Type",
        "Bucket Key",
    ]
    with open(bucketEncryptionReport, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)


# Create function to print the data into the CSV file.
def report_info(file_name, details):
    print(
        details,
        file=open(file_name, "a"),
    )


# Retrieve the default bucket encryption configuration for all buckets in specified AWS Regions.
def sse_kms_bucket_logger():
    # Initialize the Amazon S3 boto3 client for us-east-1.
    s3 = boto3.client("s3", region_name="us-east-1")
    # List all Amazon S3 buckets in the account.
    response = s3.list_buckets()
    # Retrieve the bucket name from the response
    buckets = response.get("Buckets")
    # Create a for loop to perform an action on all Amazon S3 buckets in the account.
    for bucket in buckets:
        with suppress(Exception):
            myBuckets = bucket.get("Name")
            # Sets s3 client region depending on the bucket
            response = s3.get_bucket_location(Bucket=myBuckets)
            location = response["LocationConstraint"]
            if location in regions:
                s3 = boto3.client("s3", region_name=location)
                try:
                    # Run the GetBucketEncryption on all Amazon S3 buckets in all AWS Regions.
                    resp = s3.get_bucket_encryption(Bucket=myBuckets)
                    encryption_rules = resp.get(
                        "ServerSideEncryptionConfiguration", {}
                    ).get("Rules", [])
                    if encryption_rules:
                        encryption = encryption_rules[0].get(
                            "ApplyServerSideEncryptionByDefault", {}
                        )
                        if "KMSMasterKeyID" in encryption:
                            kms_key = encryption["KMSMasterKeyID"]
                            bucketKey = str(encryption.get("BucketKeyEnabled", False))
                            report_info(
                                bucketEncryptionReport,
                                "{0}, {1}, {2}, {3}".format(
                                    myBuckets, "SSE-KMS", kms_key, bucketKey
                                ),
                            )
                        else:
                            # Handle SSE-S3 encryption
                            sse_type = encryption.get("SSEAlgorithm", "SSE-S3")
                            report_info(
                                bucketEncryptionReport,
                                "{0}, {1}, {2}".format(myBuckets, sse_type, "N/A"),
                            )
                    else:
                        # Handle case where no encryption configuration is found
                        report_info(
                            bucketEncryptionReport,
                            "{0}, {1}, {2}".format(
                                myBuckets, "SSEConfigNotFound", "N/A"
                            ),
                        )
                except s3.exceptions.ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code")
                    if error_code == "AccessDenied":
                        report_info(
                            bucketEncryptionReport,
                            "{0}, {1}, {2}, {3}".format(
                                myBuckets, "AccessDenied", "Unknown", "AccessDenied"
                            ),
                        )
                    else:
                        raise


# Execute report function.
if __name__ == "__main__":
    appendHeaders()
    sse_kms_bucket_logger()
    # Print the report's output location.
    print("")
    print("You can now access the report in the following location:  ")
    print(bucketEncryptionReport)
