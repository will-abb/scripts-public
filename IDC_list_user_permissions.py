import boto3

## ****This script assumes that permissions and accounts are managed
## through groups, not users. This will not check user access****


def fetch_instance_and_identity_store_ids(sso_client):
    """Fetch the first available Instance ID and Identity Store ID."""
    instances = sso_client.list_instances()
    if not instances["Instances"]:
        raise Exception("No SSO instances found.")
    instance = instances["Instances"][0]
    return instance["InstanceArn"], instance["IdentityStoreId"]


def list_users(identity_store_client, identity_store_id):
    """List all users in AWS Identity Center."""
    users = []
    paginator = identity_store_client.get_paginator("list_users")
    for page in paginator.paginate(IdentityStoreId=identity_store_id):
        users.extend(page["Users"])
    return users


def list_groups(identity_store_client, identity_store_id):
    """Retrieve all groups from the Identity Store."""
    groups = []
    paginator = identity_store_client.get_paginator("list_groups")
    for page in paginator.paginate(IdentityStoreId=identity_store_id):
        groups.extend(page["Groups"])
    return groups


def list_group_memberships(identity_store_client, identity_store_id, group_id):
    """List memberships for a given group."""
    memberships = []
    paginator = identity_store_client.get_paginator("list_group_memberships")
    for page in paginator.paginate(IdentityStoreId=identity_store_id, GroupId=group_id):
        memberships.extend(page["GroupMemberships"])
    return memberships


def list_permission_sets(sso_admin_client, instance_arn):
    """Retrieve all permission sets including their names, accounts, and attached policies."""
    permission_sets = {}
    paginator = sso_admin_client.get_paginator("list_permission_sets")
    for page in paginator.paginate(InstanceArn=instance_arn):
        for permission_set_arn in page["PermissionSets"]:
            detail = sso_admin_client.describe_permission_set(
                InstanceArn=instance_arn, PermissionSetArn=permission_set_arn
            )
            managed_policies = list_managed_policies_in_permission_set(
                sso_admin_client, instance_arn, permission_set_arn
            )
            customer_managed_policies = (
                list_customer_managed_policies_in_permission_set(
                    sso_admin_client, instance_arn, permission_set_arn
                )
            )
            inline_policy = get_inline_policy_for_permission_set(
                sso_admin_client, instance_arn, permission_set_arn
            )
            permission_sets[permission_set_arn] = {
                "Name": detail["PermissionSet"]["Name"],
                "Accounts": list_accounts_for_permission_set(
                    sso_admin_client, instance_arn, permission_set_arn
                ),
                "AWSManagedPolicies": managed_policies,
                "CustomerManagedPolicies": customer_managed_policies,
                "InlinePolicy": inline_policy,
            }
    return permission_sets


def list_managed_policies_in_permission_set(
    sso_admin_client, instance_arn, permission_set_arn
):
    """List all managed policies attached to a permission set."""
    policies = []
    paginator = sso_admin_client.get_paginator(
        "list_managed_policies_in_permission_set"
    )
    for page in paginator.paginate(
        InstanceArn=instance_arn, PermissionSetArn=permission_set_arn
    ):
        policies.extend([policy["Name"] for policy in page["AttachedManagedPolicies"]])
    return policies


def get_inline_policy_for_permission_set(
    sso_admin_client, instance_arn, permission_set_arn
):
    """Retrieve the inline policy attached to a permission set."""
    try:
        response = sso_admin_client.get_inline_policy_for_permission_set(
            InstanceArn=instance_arn, PermissionSetArn=permission_set_arn
        )
        return response.get(
            "InlinePolicy", ""
        )  # Return an empty string if no inline policy is found
    except Exception as e:
        print(f"Error retrieving inline policy: {e}")
        return ""


def list_customer_managed_policies_in_permission_set(
    sso_admin_client, instance_arn, permission_set_arn
):
    """List all customer-managed policies attached to a permission set."""
    policies = []
    try:
        paginator = sso_admin_client.get_paginator(
            "list_customer_managed_policy_references_in_permission_set"
        )
        for page in paginator.paginate(
            InstanceArn=instance_arn, PermissionSetArn=permission_set_arn
        ):
            policies.extend(
                [policy["Name"] for policy in page["CustomerManagedPolicyReferences"]]
            )
    except Exception as e:
        print(f"Error listing customer-managed policies: {e}")
    return policies


def list_accounts_for_permission_set(
    sso_admin_client, instance_arn, permission_set_arn
):
    """List all accounts for a given permission set."""
    accounts = []
    paginator = sso_admin_client.get_paginator(
        "list_accounts_for_provisioned_permission_set"
    )
    for page in paginator.paginate(
        InstanceArn=instance_arn, PermissionSetArn=permission_set_arn
    ):
        accounts.extend(page["AccountIds"])
    return accounts


def list_account_assignments_for_group(sso_admin_client, instance_arn, group_id):
    """List account assignments for a given group."""
    response = sso_admin_client.list_account_assignments_for_principal(
        InstanceArn=instance_arn, PrincipalId=group_id, PrincipalType="GROUP"
    )
    accounts = []
    for assignment in response.get("AccountAssignments", []):
        accounts.append(
            {
                "AccountId": assignment["AccountId"],
                "PermissionSetArn": assignment["PermissionSetArn"],
            }
        )
    return accounts


def get_permissions_boundary_for_permission_set(
    sso_admin_client, instance_arn, permission_set_arn
):
    """Retrieve the permissions boundary attached to a permission set."""
    try:
        response = sso_admin_client.get_permissions_boundary_for_permission_set(
            InstanceArn=instance_arn, PermissionSetArn=permission_set_arn
        )
        if "PermissionsBoundary" in response:
            boundary = response["PermissionsBoundary"]
            if "CustomerManagedPolicyReference" in boundary:
                name = boundary["CustomerManagedPolicyReference"].get(
                    "Name", "No name provided"
                )
                path = boundary["CustomerManagedPolicyReference"].get(
                    "Path", "No path provided"
                )
                return f"Customer Managed Policy: {path}{name}"
            elif "ManagedPolicyArn" in boundary:
                return f"Managed Policy ARN: {boundary['ManagedPolicyArn']}"
        return "No permissions boundary set"
    except sso_admin_client.exceptions.ResourceNotFoundException:
        return "No permissions boundary set"
    except Exception as e:
        print(f"Error retrieving permissions boundary: {e}")
        return "Failed to retrieve permissions boundary"


def main():
    sso_client = boto3.client("sso-admin")
    identity_store_client = boto3.client("identitystore")

    instance_arn, identity_store_id = fetch_instance_and_identity_store_ids(sso_client)
    users = list_users(identity_store_client, identity_store_id)
    groups = list_groups(identity_store_client, identity_store_id)
    permission_sets = list_permission_sets(sso_client, instance_arn)

    for user in users:
        print("-" * 55)
        print(
            f"User: {user['UserName']}, Email: {user.get('Emails', [{'Value': 'No email'}])[0]['Value']}"
        )

        # Determine groups this user is a member of
        user_group_ids = [
            group["GroupId"]
            for group in groups
            if any(
                m["MemberId"]["UserId"] == user["UserId"]
                for m in list_group_memberships(
                    identity_store_client, identity_store_id, group["GroupId"]
                )
            )
        ]
        print(
            f"  Groups: {', '.join([group['DisplayName'] for group in groups if group['GroupId'] in user_group_ids])}"
        )

        # Collect accounts and permissions details based on group membership
        accounts_permissions = {}
        for group_id in user_group_ids:
            group_accounts = list_account_assignments_for_group(
                sso_client, instance_arn, group_id
            )
            for account in group_accounts:
                account_id = account["AccountId"]
                if account_id not in accounts_permissions:
                    accounts_permissions[account_id] = {
                        "PermissionSets": [],
                        "AWSManagedPolicies": set(),
                        "CustomerManagedPolicies": set(),
                        "InlinePolicies": set(),
                        "PermissionsBoundary": "No permissions boundary set",
                    }

                for permission_set_arn in (
                    account["PermissionSetArn"]
                    if isinstance(account["PermissionSetArn"], list)
                    else [account["PermissionSetArn"]]
                ):
                    if permission_set_arn in permission_sets:
                        perm_set = permission_sets[permission_set_arn]
                        accounts_permissions[account_id]["PermissionSets"].append(
                            perm_set["Name"]
                        )
                        accounts_permissions[account_id]["AWSManagedPolicies"].update(
                            perm_set.get("AWSManagedPolicies", [])
                        )
                        accounts_permissions[account_id][
                            "CustomerManagedPolicies"
                        ].update(perm_set.get("CustomerManagedPolicies", []))
                        if perm_set.get("InlinePolicy"):
                            accounts_permissions[account_id]["InlinePolicies"].add(
                                perm_set["InlinePolicy"]
                            )
                        boundary_info = get_permissions_boundary_for_permission_set(
                            sso_client, instance_arn, permission_set_arn
                        )
                        if boundary_info != "No permissions boundary set":
                            accounts_permissions[account_id][
                                "PermissionsBoundary"
                            ] = boundary_info

        # Print account details only for accounts associated with user's groups
        for account_id, details in accounts_permissions.items():
            print(f"    Account ID: {account_id}")
            print(f"      Permissions Boundary: {details['PermissionsBoundary']}")
            print(
                f"      Permission Sets: {', '.join(details['PermissionSets']) if details['PermissionSets'] else 'None'}"
            )
            print(
                f"      AWS Managed Policies: {', '.join(details['AWSManagedPolicies']) if details['AWSManagedPolicies'] else 'None'}"
            )
            print(
                f"      Customer Managed Policies: {', '.join(details['CustomerManagedPolicies']) if details['CustomerManagedPolicies'] else 'None'}"
            )
            print(
                f"      Inline Policy: {', '.join(details['InlinePolicies']) if details['InlinePolicies'] else 'None'}"
            )


if __name__ == "__main__":
    main()
