import logging
import boto3
import re

logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_users():
    iam = boto3.client("iam")
    paginator = iam.get_paginator("list_users")
    users = []
    for page in paginator.paginate():
        for user in page["Users"]:
            users.append(user["UserName"])
    return users


def get_groups():
    iam = boto3.client("iam")
    paginator = iam.get_paginator("list_groups")
    groups = []
    for page in paginator.paginate():
        for group in page["Groups"]:
            groups.append(group["GroupName"])
    return groups


def get_roles():
    iam = boto3.client("iam")
    paginator = iam.get_paginator("list_roles")
    roles = []
    for page in paginator.paginate():
        for role in page["Roles"]:
            roles.append(role["RoleName"])
    return roles


def get_managed_policies(entity_name, entity_type):
    iam = boto3.client("iam")
    if entity_type == "user":
        attached_policies = iam.list_attached_user_policies(UserName=entity_name)[
            "AttachedPolicies"
        ]
    elif entity_type == "role":
        attached_policies = iam.list_attached_role_policies(RoleName=entity_name)[
            "AttachedPolicies"
        ]
    elif entity_type == "group":
        attached_policies = iam.list_attached_group_policies(GroupName=entity_name)[
            "AttachedPolicies"
        ]
    managed_policies = [policy["PolicyArn"] for policy in attached_policies]
    return managed_policies


def get_inline_policies(entity_name, entity_type):
    iam = boto3.client("iam")
    if entity_type == "user":
        inline_policy_names = iam.list_user_policies(UserName=entity_name)[
            "PolicyNames"
        ]
    elif entity_type == "role":
        inline_policy_names = iam.list_role_policies(RoleName=entity_name)[
            "PolicyNames"
        ]
    elif entity_type == "group":
        inline_policy_names = iam.list_group_policies(GroupName=entity_name)[
            "PolicyNames"
        ]
    policies = []
    for policy_name in inline_policy_names:
        if entity_type == "user":
            policy_doc = iam.get_user_policy(
                UserName=entity_name, PolicyName=policy_name
            )["PolicyDocument"]
        elif entity_type == "role":
            policy_doc = iam.get_role_policy(
                RoleName=entity_name, PolicyName=policy_name
            )["PolicyDocument"]
        elif entity_type == "group":
            policy_doc = iam.get_group_policy(
                GroupName=entity_name, PolicyName=policy_name
            )["PolicyDocument"]
        policies.append((policy_name, policy_doc))
    return policies


def get_permission_boundaries(entity_name, entity_type):
    iam = boto3.client("iam")
    entity = None
    if entity_type == "user":
        entity = iam.get_user(UserName=entity_name)["User"]
    elif entity_type == "role":
        entity = iam.get_role(RoleName=entity_name)["Role"]
    if entity:
        permission_boundary = entity.get("PermissionsBoundary", {}).get(
            "PermissionsBoundaryArn"
        )
        return permission_boundary
    else:
        return None


def extract_root_action(action):
    action_without_service = re.sub(r"^[a-z0-9]+:", "", action)
    action_without_wildcard = re.sub(r"\*", "", action_without_service)
    match = re.match(r"([A-Z][a-z]+)", action_without_wildcard)
    return match.group(1) if match else action_without_wildcard


def extract_service(action):
    match = re.match(r"([a-z0-9]+):", action)
    return match.group(1) if match else None


def is_full_admin(action):
    if action in ["*:*", "*"]:
        return True
    return False


def is_service_admin(action, service):
    if action == f"{service}:*":
        return True
    return False


def is_exact_permission(action, service, permissions):
    if action == f"{service}:{permissions}":
        return True
    return False


def is_permission_with_wildcard(action, service, permission_root):
    if "*" in action and action.startswith(f"{service}:"):
        extracted_root_action = extract_root_action(action)
        if extracted_root_action == permission_root:
            return True
    return False


def validate_policy_statement(statement):
    if (
        isinstance(statement, dict)
        and "Effect" in statement
        and statement["Effect"] == "Allow"
        and "Action" in statement
    ):
        actions = statement["Action"]
        if not isinstance(actions, list):
            actions = [actions]
        return True, actions
    return False, []


def validate_and_format_policy(policy, permissions):
    if "Statement" not in policy:
        return False, None, None
    permission_root = extract_root_action(permissions)
    return True, policy["Statement"], permission_root


def has_service_access(policy, service, permissions_list):
    valid_policy, policy_statements, permission_root = validate_and_format_policy(
        policy, permissions_list[0]
    )
    if not valid_policy:
        return False, False, False
    for statement in policy_statements:
        valid_statement, actions = validate_policy_statement(statement)
        if not valid_statement:
            continue

        for action in actions:
            action_service = extract_service(action)

            if is_full_admin(action):
                return True, False, True  # Full admin policy

            if action_service != service:
                continue

            action_root = extract_root_action(action)

            if is_service_admin(action, service):
                return True, True, False  # Service admin policy

            for permissions in permissions_list:
                if is_exact_permission(action, service, permissions):
                    return True, False, False

                if is_permission_with_wildcard(action, service, permission_root):
                    return True, False, False
    return False, False, False


def analyze_policies(
    policies, iam, service, permissions, policy_type, entity_name, entity_type
):
    policies_with_access = []
    permissions_list = permissions.split(",")
    for policy in policies:
        if isinstance(policy, str):  # Managed policies or permission boundary
            policy_doc = iam.get_policy_version(
                PolicyArn=policy,
                VersionId=iam.get_policy(PolicyArn=policy)["Policy"][
                    "DefaultVersionId"
                ],
            )["PolicyVersion"]["Document"]
            policy_identifier = policy
        else:  # Inline policies
            policy_name, policy_doc = policy
            policy_identifier = policy_name

        has_access, is_service_admin_policy, is_full_admin_policy = has_service_access(
            policy_doc, service, permissions_list
        )
        if has_access:
            policies_with_access.append(f"{policy_type}: {policy_identifier}")
            if is_full_admin_policy:
                policies_with_access.append(
                    f" - Note: This policy grants full admin access."
                )
            if is_service_admin_policy:
                policies_with_access.append(
                    f" - Note: This policy grants {service} admin access."
                )
    return policies_with_access
