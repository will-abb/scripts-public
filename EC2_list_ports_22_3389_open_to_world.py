import argparse
import boto3


def check_security_groups(profile=None):
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    ec2 = session.client("ec2")

    security_groups = ec2.describe_security_groups()["SecurityGroups"]
    counter = 0

    for sg in security_groups:
        sg_id = sg["GroupId"]
        sg_name = sg["GroupName"]
        sg_description = sg.get("Description", "No description")
        ingress_rules = sg["IpPermissions"]

        for rule in ingress_rules:
            ip_protocol = rule.get("IpProtocol", None)
            from_port = rule.get("FromPort", None)
            to_port = rule.get("ToPort", None)
            ip_ranges = rule.get("IpRanges", [])

            if ip_protocol == "-1":
                counter += 1
                print(f"\n{counter}. Security Group Details:")
                print(f"   Group Name: {sg_name}")
                print(f"   Group ID: {sg_id}")
                print(f"   Description: {sg_description}")
                print("   Allows All Traffic on all ports")

            elif from_port is not None and to_port is not None:
                for ip_range in ip_ranges:
                    cidr_ip = ip_range.get("CidrIp")
                    if cidr_ip == "0.0.0.0/0":
                        if from_port <= 22 <= to_port or from_port <= 3389 <= to_port:
                            counter += 1
                            print(f"\n{counter}. Security Group Details:")
                            print(f"   Group Name: {sg_name}")
                            print(f"   Group ID: {sg_id}")
                            print(f"   Description: {sg_description}")
                            print(
                                f"   Allows inbound access from 0.0.0.0/0 to port range {from_port}-{to_port}"
                            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check AWS Security Groups for risky ingress rules."
    )
    parser.add_argument("--profile", type=str, help="AWS CLI profile to use")
    args = parser.parse_args()

    check_security_groups(profile=args.profile)
