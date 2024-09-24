#!/usr/bin/env python3
import boto3

# The purpose of the script is to be able to find what/who  has access to
# log into an instance in an environment where only SSM sessions are the
# only way to do so.


# Function to retrieve all users and their attached policies
def get_users_and_attached_policies():
    iam = boto3.client("iam")
    paginator = iam.get_paginator("list_users")
    users = []
    user_attached_policies = {}
    for page in paginator.paginate():
        for user in page["Users"]:
            users.append(user)
            policies = iam.list_attached_user_policies(UserName=user["UserName"])
            user_attached_policies[user["UserName"]] = [
                policy["PolicyArn"] for policy in policies["AttachedPolicies"]
            ]
    return users, user_attached_policies


# Function to retrieve all groups and the groups that users belong to
def get_groups_and_user_groups():
    iam = boto3.client("iam")
    paginator = iam.get_paginator("list_groups")
    groups = {}
    user_groups = {}
    for page in paginator.paginate():
        for group in page["Groups"]:
            groups[group["GroupName"]] = group
            group_policies = iam.list_attached_group_policies(
                GroupName=group["GroupName"]
            )
            group["AttachedManagedPolicies"] = [
                policy["PolicyArn"] for policy in group_policies["AttachedPolicies"]
            ]
            for user in iam.get_group(GroupName=group["GroupName"])["Users"]:
                if user["UserName"] not in user_groups:
                    user_groups[user["UserName"]] = []
                user_groups[user["UserName"]].append(group["GroupName"])
    return groups, user_groups


# Function to retrieve all managed policies
def get_managed_policies():
    iam = boto3.client("iam")
    paginator = iam.get_paginator("list_policies")
    policies = {}
    for page in paginator.paginate(Scope="All"):
        for policy in page["Policies"]:
            if policy["Arn"] not in policies:
                policies[policy["Arn"]] = iam.get_policy_version(
                    PolicyArn=policy["Arn"], VersionId=policy["DefaultVersionId"]
                )["PolicyVersion"]["Document"]
    return policies


# Function to check if a user has admin access through a group
def is_user_admin_through_group(user, groups, policies, user_groups):
    if user["UserName"] not in user_groups:
        return False

    for group_name in user_groups[user["UserName"]]:
        group = groups[group_name]
        for policy_arn in group["AttachedManagedPolicies"]:
            if has_admin_access(policies[policy_arn]):
                return True

    return False


# Function to check if a user has Session Manager access through a group
def does_user_have_session_manager_access_through_group(
    user, groups, policies, user_groups
):
    if user["UserName"] not in user_groups:
        return False

    for group_name in user_groups[user["UserName"]]:
        group = groups[group_name]
        for policy_arn in group["AttachedManagedPolicies"]:
            if has_session_manager_access(policies[policy_arn]):
                return True

    return False


# Function to check if a policy has admin access
def has_admin_access(policy):
    if "Statement" not in policy:
        return False

    for statement in policy["Statement"]:
        if (
            isinstance(statement, dict)
            and "Effect" in statement
            and statement["Effect"] == "Allow"
            and "Action" in statement
            and statement["Action"] == "*"
            and "Resource" in statement
            and statement["Resource"] == "*"
        ):
            return True
    return False


# Function to check if a policy has Session Manager access
def has_session_manager_access(policy):
    if "Statement" not in policy:
        return False

    for statement in policy["Statement"]:
        if (
            isinstance(statement, dict)
            and "Effect" in statement
            and statement["Effect"] == "Allow"
            and "Action" in statement
            and any(
                action in ["ssm:StartSession", "ssm:*", "*"]
                for action in (
                    statement["Action"]
                    if isinstance(statement["Action"], list)
                    else [statement["Action"]]
                )
            )
            and "Resource" in statement
            and any(
                r.startswith("arn:aws:ssm:") or r == "*"
                for r in (
                    statement["Resource"]
                    if isinstance(statement["Resource"], list)
                    else [statement["Resource"]]
                )
            )
        ):
            return True
    return False


# Function to analyze inline policies for admin and Session Manager access
def analyze_inline_policies(policy_document, iam_entity_type, entity_name):
    admin_entities = []
    session_manager_entities = []
    if has_admin_access(policy_document):
        admin_entities.append(entity_name)
    if has_session_manager_access(policy_document):
        session_manager_entities.append(entity_name)
    return admin_entities, session_manager_entities


# Function to analyze attached policies for admin and Session Manager access
def analyze_attached_policies(policy_arns, iam, iam_entity_type, entity_name):
    admin_users = []
    session_manager_users = []
    for policy_arn in policy_arns:
        policy = iam.get_policy_version(
            PolicyArn=policy_arn,
            VersionId=iam.get_policy(PolicyArn=policy_arn)["Policy"][
                "DefaultVersionId"
            ],
        )["PolicyVersion"]["Document"]
        if has_admin_access(policy):
            admin_users.append(entity_name)
        if has_session_manager_access(policy):
            session_manager_users.append(entity_name)
    return admin_users, session_manager_users


# Function to check if a user has admin access
def has_user_admin_access(user, policies, user_attached_policies, groups, user_groups):
    username = user["UserName"]

    for policy_arn in user_attached_policies.get(username, []):
        if has_admin_access(policies[policy_arn]):
            return True

    return is_user_admin_through_group(user, groups, policies, user_groups)


# Function to check if a user has Session Manager access
def has_user_session_manager_access(
    user, policies, user_attached_policies, groups, user_groups
):
    username = user["UserName"]

    for policy_arn in user_attached_policies.get(username, []):
        if has_session_manager_access(policies[policy_arn]):
            return True

    return does_user_have_session_manager_access_through_group(
        user, groups, policies, user_groups
    )


# Function to retrieve all roles and their attached policies
def get_roles_and_attached_policies():
    iam = boto3.client("iam")
    paginator = iam.get_paginator("list_roles")
    roles = []
    role_attached_policies = {}
    role_inline_policies = {}
    for page in paginator.paginate():
        for role in page["Roles"]:
            roles.append(role)
            policies = iam.list_attached_role_policies(RoleName=role["RoleName"])
            role_attached_policies[role["RoleName"]] = [
                policy["PolicyArn"] for policy in policies["AttachedPolicies"]
            ]
            inline_policies = iam.list_role_policies(RoleName=role["RoleName"])[
                "PolicyNames"
            ]
            for inline_policy in inline_policies:
                inline_policy_document = iam.get_role_policy(
                    RoleName=role["RoleName"], PolicyName=inline_policy
                )["PolicyDocument"]
                if role["RoleName"] not in role_inline_policies:
                    role_inline_policies[role["RoleName"]] = []
                role_inline_policies[role["RoleName"]].append(inline_policy_document)
    return roles, role_attached_policies, role_inline_policies


# Function to check if a role has admin access
def has_role_admin_access(role, policies, role_attached_policies, role_inline_policies):
    rolename = role["RoleName"]

    for policy_arn in role_attached_policies.get(rolename, []):
        if has_admin_access(policies[policy_arn]):
            return True

    for inline_policy in role_inline_policies.get(rolename, []):
        if has_admin_access(inline_policy):
            return True

    return False


# Function to check if a role has Session Manager access
def has_role_session_manager_access(
    role, policies, role_attached_policies, role_inline_policies
):
    rolename = role["RoleName"]

    for policy_arn in role_attached_policies.get(rolename, []):
        if has_session_manager_access(policies[policy_arn]):
            return True

    for inline_policy in role_inline_policies.get(rolename, []):
        if has_session_manager_access(inline_policy):
            return True

    return False


# Main function
def main():
    # Retrieve all users and attached policies
    users, user_attached_policies = get_users_and_attached_policies()
    # Retrieve all groups and user groups
    groups, user_groups = get_groups_and_user_groups()
    # Retrieve all roles and attached policies
    (
        roles,
        role_attached_policies,
        role_inline_policies,
    ) = get_roles_and_attached_policies()
    # Retrieve all managed policies
    policies = get_managed_policies()

    # Output users with admin or Session Manager access
    print("\n=== Users ===\n")
    for user in users:
        username = user["UserName"]
        user_admin = has_user_admin_access(
            user, policies, user_attached_policies, groups, user_groups
        )
        user_session_manager = has_user_session_manager_access(
            user, policies, user_attached_policies, groups, user_groups
        )

        if user_admin or user_session_manager:
            print(f"{username}:")
            print(f"  {'Admin' if user_admin else 'Not Admin'}")
            print(
                f"  {'Session Manager' if user_session_manager else 'Not Session Manager'}"
            )

    # Output roles with admin or Session Manager access
    print("\n=== Roles ===\n")
    for role in roles:
        rolename = role["RoleName"]
        role_admin = has_role_admin_access(
            role, policies, role_attached_policies, role_inline_policies
        )
        role_session_manager = has_role_session_manager_access(
            role, policies, role_attached_policies, role_inline_policies
        )

        if role_admin or role_session_manager:
            print(f"{rolename}:")
            print(f"  {'Admin' if role_admin else 'Not Admin'}")
            print(
                f"  {'Session Manager' if role_session_manager else 'Not Session Manager'}"
            )


# Entry point for script execution
if __name__ == "__main__":
    main()
