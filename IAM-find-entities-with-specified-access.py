# #!/usr/bin/env python3
# import boto3
# import argparse
# import logging

# # Setup logging
# logging.basicConfig(level=logging.INFO, format="%(message)s")

# # Function to retrieve all users
# def get_users():
#     iam = boto3.client("iam")
#     paginator = iam.get_paginator("list_users")
#     users = []
#     for page in paginator.paginate():
#         for user in page["Users"]:
#             users.append(user["UserName"])
#     return users


# # Function to get managed policies attached to a user (both AWS and customer-managed)
# def get_managed_policies(user_name):
#     iam = boto3.client("iam")
#     attached_policies = iam.list_attached_user_policies(UserName=user_name)[
#         "AttachedPolicies"
#     ]
#     managed_policies = [policy["PolicyArn"] for policy in attached_policies]
#     logging.info(f"User: {user_name}, Managed Policies: {managed_policies}")
#     return managed_policies


# # Function to get inline policies attached to a user
# def get_inline_policies(user_name):
#     iam = boto3.client("iam")
#     inline_policies = iam.list_user_policies(UserName=user_name)["PolicyNames"]
#     policies = []
#     for policy_name in inline_policies:
#         policy_doc = iam.get_user_policy(UserName=user_name, PolicyName=policy_name)[
#             "PolicyDocument"
#         ]
#         policies.append(policy_doc)
#     logging.info(f"User: {user_name}, Inline Policies: {inline_policies}")
#     return policies


# # Function to get permission boundaries of a user
# def get_permission_boundaries(user_name):
#     iam = boto3.client("iam")
#     user = iam.get_user(UserName=user_name)["User"]
#     permission_boundary = user.get("PermissionsBoundary", {}).get(
#         "PermissionsBoundaryArn"
#     )
#     logging.info(f"User: {user_name}, Permission Boundary: {permission_boundary}")
#     return permission_boundary


# # Function to check if a policy has the specified service permissions
# def has_service_access(policy, service, permissions):
#     if "Statement" not in policy:
#         return False
#     for statement in policy["Statement"]:
#         if (
#             isinstance(statement, dict)
#             and "Effect" in statement
#             and statement["Effect"] == "Allow"
#             and "Action" in statement
#         ):
#             actions = statement["Action"]
#             if not isinstance(actions, list):
#                 actions = [actions]
#             for action in actions:
#                 if (
#                     action == "*:*"
#                     or action == f"{service}:*"
#                     or action == f"{service}:{permissions}"
#                 ):
#                     return True
#     return False


# # Function to check if a policy grants full admin access
# def has_full_admin_access(policy):
#     if "Statement" not in policy:
#         return False
#     for statement in policy["Statement"]:
#         if (
#             isinstance(statement, dict)
#             and "Effect" in statement
#             and statement["Effect"] == "Allow"
#             and ("*" in statement["Action"] or statement["Action"] == "*:*")
#         ):
#             return True
#     return False


# # Function to analyze policies for specified service access
# def analyze_policies(policies, iam, service, permissions, policy_type):
#     policies_with_access = []
#     for policy in policies:
#         if isinstance(policy, str):  # Managed policies or permission boundary
#             policy_doc = iam.get_policy_version(
#                 PolicyArn=policy,
#                 VersionId=iam.get_policy(PolicyArn=policy)["Policy"][
#                     "DefaultVersionId"
#                 ],
#             )["PolicyVersion"]["Document"]
#         else:  # Inline policies
#             policy_doc = policy

#         policy_has_access = has_service_access(
#             policy_doc, service, permissions
#         ) or has_full_admin_access(policy_doc)
#         logging.info(
#             f"Checking {policy_type}: {policy} - Has access: {policy_has_access}"
#         )

#         if policy_has_access:
#             policies_with_access.append(
#                 f"{policy_type}: {policy}"
#                 if isinstance(policy, str)
#                 else f"{policy_type}"
#             )
#     return policies_with_access


# # Main function
# def main(service, permissions, single_user):
#     iam = boto3.client("iam")

#     # Retrieve users
#     users = [single_user] if single_user else get_users()

#     service_users = {}

#     # Analyze user policies
#     for user_name in users:
#         managed_policies = get_managed_policies(user_name)
#         inline_policies = get_inline_policies(user_name)
#         permission_boundary = get_permission_boundaries(user_name)

#         managed_policies_with_access = analyze_policies(
#             managed_policies, iam, service, permissions, "Managed Policy"
#         )
#         inline_policies_with_access = analyze_policies(
#             inline_policies, iam, service, permissions, "Inline Policy"
#         )
#         permission_boundary_with_access = (
#             analyze_policies(
#                 [permission_boundary], iam, service, permissions, "Permission Boundary"
#             )
#             if permission_boundary
#             else []
#         )

#         policies_with_access = (
#             managed_policies_with_access
#             + inline_policies_with_access
#             + permission_boundary_with_access
#         )

#         if policies_with_access:
#             service_users[user_name] = policies_with_access

#     # Print results
#     for user, policies in service_users.items():
#         print(f"\nUser: {user}")
#         for policy in policies:
#             print(f" - {policy}")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Find users with specified service access."
#     )
#     parser.add_argument(
#         "--service", required=True, help="The AWS service to check (e.g., s3)."
#     )
#     parser.add_argument(
#         "--permissions",
#         required=True,
#         help="The permissions to check (e.g., GetObject).",
#     )
#     parser.add_argument("--user", help="Specify a single user to check.")
#     args = parser.parse_args()
#     main(args.service, args.permissions, args.user)
