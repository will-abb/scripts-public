import boto3


def list_trails_and_log_groups():
    """
    List all CloudTrail trails and their associated CloudWatch Logs log groups.
    """
    # Create a CloudTrail client
    client = boto3.client("cloudtrail")

    # Call describe_trails to fetch trail details
    response = client.describe_trails()

    # Print the output
    print("Describing trails and their associated log groups:")
    for trail in response["trailList"]:
        name = trail.get("Name", "No Name Specified")
        log_group = trail.get("CloudWatchLogsLogGroupArn", "No Log Group Specified")
        print(f"Trail Name: {name}, Log Group: {log_group}")


if __name__ == "__main__":
    list_trails_and_log_groups()
