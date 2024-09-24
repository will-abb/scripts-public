import boto3
import json
import re


def list_cmk_administrators():
    kms_client = boto3.client("kms")
    response = kms_client.list_keys()
    keys = response["Keys"]

    cmks = []
    for key_info in keys:
        key_id = key_info["KeyId"]
        key_metadata = kms_client.describe_key(KeyId=key_id)
        if key_metadata["KeyMetadata"]["KeyManager"] == "CUSTOMER":
            cmks.append(key_info)

    management_actions = {
        "kms:CancelKeyDeletion",
        "kms:Create*",
        "kms:Delete*",
        "kms:Disable*",
        "kms:Enable*",
        "kms:GenerateDataKey*",
        "kms:ImportKeyMaterial",
        "kms:PutKeyPolicy",
        "kms:ScheduleKeyDeletion",
        "kms:UpdateAlias",
        "kms:UpdateCustomKeyStore",
        "kms:UpdatePrimaryRegion",
        "kms:CreateGrant",
        "kms:RevokeGrant",
        "kms:RetireGrant",
        "*",
    }

    key_admins = {}

    for key in cmks:
        key_id = key["KeyId"]
        policy = kms_client.get_key_policy(KeyId=key_id, PolicyName="default")
        policy_dict = json.loads(policy["Policy"])

        admins = []
        full_iam_access = False  # Initialize as False for each key

        for statement in policy_dict["Statement"]:
            principal_aws = statement.get("Principal", {}).get("AWS", "") or ""
            if isinstance(principal_aws, list):  # Handle multiple AWS principals
                for single_principal in principal_aws:
                    full_iam_access |= check_and_add_principal(
                        single_principal, statement, admins, management_actions
                    )
            else:  # Handle a single AWS principal
                full_iam_access |= check_and_add_principal(
                    principal_aws, statement, admins, management_actions
                )

        key_admins[key_id] = {"admins": admins, "full_iam_access": full_iam_access}

    return key_admins


def check_and_add_principal(principal_aws, statement, admins, management_actions):
    full_access = False
    if (
        statement["Effect"] == "Allow"
        and re.match(r"arn:aws:iam::\d+:root", principal_aws)
        and statement["Action"] == "kms:*"
    ):
        full_access = True  # Set this if the condition is met

    if statement["Effect"] == "Allow":
        actions = statement["Action"]
        if not isinstance(actions, list):
            actions = [actions]
        if set(actions) & management_actions or "*" in actions:
            admins.append(principal_aws)

    return full_access  # Return whether full access is granted


def main():
    admins_by_key = list_cmk_administrators()
    for key_id, admin_info in admins_by_key.items():
        print(f"Key ID: {key_id}")
        if admin_info["full_iam_access"]:
            print("WARNING: This key allows full management access through IAM.")
        if admin_info["admins"]:
            print("Administrators with management access:")
            for admin in admin_info["admins"]:
                print(f"  {admin}")
        else:
            print("No specific administrators with limited management access listed.")

        print("-" * 70)  # Print a dashed line after each key's information


if __name__ == "__main__":
    main()
