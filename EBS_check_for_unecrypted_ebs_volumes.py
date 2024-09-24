import boto3


def get_default_ebs_encryption(client):
    """
    Check if the account has EBS encryption by default enabled.
    """
    try:
        response = client.get_ebs_encryption_by_default()
        return response["EbsEncryptionByDefault"]
    except Exception as e:
        print(f"Error checking default EBS encryption: {e}")
        return None


def list_unencrypted_volumes(client):
    """
    List all EBS volumes that are not encrypted.
    """
    unencrypted_volumes = []
    try:
        paginator = client.get_paginator("describe_volumes")
        for page in paginator.paginate():
            for volume in page["Volumes"]:
                if not volume["Encrypted"]:
                    unencrypted_volumes.append(volume["VolumeId"])
    except Exception as e:
        print(f"Error listing volumes: {e}")

    return unencrypted_volumes


def main():
    """
    The main function to check EBS encryption settings and list unencrypted volumes.
    """
    # Create an EC2 client
    client = boto3.client("ec2")

    # Check and print whether encryption by default is enabled
    encryption_by_default = get_default_ebs_encryption(client)
    if encryption_by_default is not None:
        print(
            f"EBS Encryption by Default is {'enabled' if encryption_by_default else 'disabled'}."
        )

    # List and print unencrypted EBS volumes
    unencrypted_volumes = list_unencrypted_volumes(client)
    if unencrypted_volumes:
        print("Unencrypted EBS Volumes:")
        print(", ".join(unencrypted_volumes))
    else:
        print("No unencrypted EBS volumes found.")


if __name__ == "__main__":
    main()
