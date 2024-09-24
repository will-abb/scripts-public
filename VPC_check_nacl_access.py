import argparse
import boto3


def check_nacls():
    client = boto3.client("ec2")
    response = client.describe_network_acls()
    nacls = response["NetworkAcls"]

    for nacl in nacls:
        nacl_id = nacl["NetworkAclId"]
        entries = sorted(nacl["Entries"], key=lambda x: x["RuleNumber"])

        print(f"\nNACL ID: {nacl_id}")

        for entry in entries:
            rule_number = entry["RuleNumber"]
            rule_action = entry["RuleAction"]
            protocol = entry["Protocol"]
            cidr_block = entry.get("CidrBlock", entry.get("Ipv6CidrBlock"))

            protocol_name = "all" if protocol == "-1" else protocol

            if rule_action == "allow" or (
                rule_action == "deny" and rule_number != 32767
            ):
                print(
                    f"Rule {rule_number}: Action: {rule_action.upper()}, Protocol: {protocol_name}, CIDR: {cidr_block}"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check NACLs for allow and non-default deny rules configurations."
    )
    args = parser.parse_args()
    check_nacls()
