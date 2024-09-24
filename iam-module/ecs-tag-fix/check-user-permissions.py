import argparse
import logging
import boto3
from iam_utils import (
    get_users,
    get_managed_policies,
    get_inline_policies,
    get_permission_boundaries,
    analyze_policies,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Main function
def main(service, permissions, single_user=None):
    iam = boto3.client("iam")

    # Split permissions into a list
    permissions_list = permissions.split(",")

    # Retrieve users
    users = [single_user] if single_user else get_users()
    # logging.info(f"Users to be checked: {users}")

    service_users = {}

    # Analyze user policies
    for user_name in users:
        # logging.info(f"Analyzing policies for user: {user_name}")

        managed_policies = get_managed_policies(user_name, "user")
        # logging.info(f"Managed policies for {user_name}: {managed_policies}")

        inline_policies = get_inline_policies(user_name, "user")
        # logging.info(f"Inline policies for {user_name}: {inline_policies}")

        permission_boundary = get_permission_boundaries(user_name, "user")
        # logging.info(f"Permission boundary for {user_name}: {permission_boundary}")

        policies_with_access = set()

        for permission in permissions_list:
            managed_policies_with_access = analyze_policies(
                managed_policies,
                iam,
                service,
                permission,
                "Managed Policy",
                user_name,
                "user",
            )
            inline_policies_with_access = analyze_policies(
                inline_policies,
                iam,
                service,
                permission,
                "Inline Policy",
                user_name,
                "user",
            )
            permission_boundary_with_access = (
                analyze_policies(
                    [permission_boundary],
                    iam,
                    service,
                    permission,
                    "Permission Boundary",
                    user_name,
                    "user",
                )
                if permission_boundary
                else []
            )

            policies_with_access.update(
                managed_policies_with_access
                + inline_policies_with_access
                + permission_boundary_with_access
            )

        if policies_with_access:
            service_users[user_name] = list(policies_with_access)

    # Print results
    for user, policies in service_users.items():
        print(f"\nUser: {user}")
        print("Policies with Access:")
        for policy in policies:
            print(f" - {policy}")

    logging.info(
        "Be advised that this only checks for permissions directly attached to the user. It does not check for permissions given through roles or through groups."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find users with specified service access."
    )
    parser.add_argument(
        "--service", required=True, help="The AWS service to check (e.g., ecs)."
    )
    parser.add_argument(
        "--permissions",
        required=True,
        help="The permissions to check (e.g., CreateCapacityProvider,CreateCluster,CreateService,CreateTaskSet,RegisterContainerInstance,RegisterTaskDefinition,RunTask,StartTask).",
    )
    parser.add_argument("--user", help="Specify a single user to check.")
    args = parser.parse_args()
    main(args.service, args.permissions, args.user)
