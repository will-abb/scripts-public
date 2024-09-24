import boto3


def list_vpcs(ec2_client):
    """List all VPCs in the current AWS account."""
    try:
        vpcs = ec2_client.describe_vpcs()
        return vpcs["Vpcs"]
    except Exception as e:
        print(f"Error listing VPCs: {e}")
        return []


def check_flow_logs(ec2_client, vpc_id):
    """Check if there are Flow Logs enabled for the specified VPC."""
    try:
        flow_logs = ec2_client.describe_flow_logs(
            Filters=[{"Name": "resource-id", "Values": [vpc_id]}]
        )
        return "ENABLED" if flow_logs["FlowLogs"] else "DISABLED"
    except Exception as e:
        print(f"Error checking Flow Logs for VPC {vpc_id}: {e}")
        return "ERROR"


def main():
    """Main function to check VPC Flow Logs status."""
    ec2_client = boto3.client("ec2")

    vpcs = list_vpcs(ec2_client)
    if not vpcs:
        print("No VPCs found in this account.")
        return

    for vpc in vpcs:
        vpc_id = vpc["VpcId"]
        status = check_flow_logs(ec2_client, vpc_id)
        print(f"VPC ID: {vpc_id}, Flow Logs Status: {status}")


if __name__ == "__main__":
    main()
