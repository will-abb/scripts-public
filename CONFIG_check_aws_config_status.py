import boto3


def check_aws_config():
    """
    Check AWS Config to ensure it is actively recording and has an S3 bucket destination.
    It also lists all the enabled AWS Config rules.
    """
    separator = "=" * 50
    print(f"{separator}\nChecking AWS Config status...\n{separator}")

    # Initialize Boto3 client for AWS Config
    config_service = boto3.client("config")

    # List AWS Config rules
    print("Enabled Config Rules:")
    try:
        config_rules = config_service.describe_config_rules()
        for rule in config_rules["ConfigRules"]:
            print(f"{rule['ConfigRuleName']}: {rule['ConfigRuleState']}")
    except Exception as e:
        print("Failed to retrieve Config rules:", str(e))
    print(separator)

    # Check Config recorder settings
    print("Configuration Recorder Status:")
    try:
        recorder_status = config_service.describe_configuration_recorder_status()
        if recorder_status["ConfigurationRecordersStatus"]:
            status = recorder_status["ConfigurationRecordersStatus"][0]
            print(
                f"Configuration Recorder is {'active' if status['recording'] else 'inactive'}."
            )
        else:
            print("No Configuration Recorder found.")
    except Exception as e:
        print("Failed to retrieve Config recorder settings:", str(e))
    print(separator)

    # Check if there is a delivery channel configured with an S3 bucket
    print("S3 Bucket Configuration for Config Logs:")
    try:
        delivery_channels = config_service.describe_delivery_channels()
        if delivery_channels["DeliveryChannels"]:
            s3_bucket = delivery_channels["DeliveryChannels"][0]["s3BucketName"]
            print(f"Config logs are sent to S3 bucket: {s3_bucket}")
        else:
            print("No S3 bucket destination is configured for Config logs.")
    except Exception as e:
        print("Failed to check delivery channels:", str(e))
    print(separator)


def main():
    check_aws_config()


if __name__ == "__main__":
    main()
