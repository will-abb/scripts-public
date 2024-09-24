import argparse
import logging
import boto3
from iam_utils import (
    get_roles,
    get_managed_policies,
    get_inline_policies,
    get_permission_boundaries,
    analyze_policies,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Main function
def main(service, permissions, single_role=None):
    iam = boto3.client("iam")

    # Split permissions into a list
    permissions_list = permissions.split(",")

    # Retrieve roles
    roles = [single_role] if single_role else get_roles()
    # logging.info(f"Roles to be checked: {roles}")

    service_roles = {}

    # Analyze role policies
    for role_name in roles:
        # logging.info(f"Analyzing policies for role: {role_name}")

        managed_policies = get_managed_policies(role_name, "role")
        # logging.info(f"Managed policies for {role_name}: {managed_policies}")

        inline_policies = get_inline_policies(role_name, "role")
        # logging.info(f"Inline policies for {role_name}: {inline_policies}")

        permission_boundary = get_permission_boundaries(role_name, "role")
        # logging.info(f"Permission boundary for {role_name}: {permission_boundary}")

        policies_with_access = set()

        for permission in permissions_list:
            managed_policies_with_access = analyze_policies(
                managed_policies,
                iam,
                service,
                permission,
                "Managed Policy",
                role_name,
                "role",
            )
            inline_policies_with_access = analyze_policies(
                inline_policies,
                iam,
                service,
                permission,
                "Inline Policy",
                role_name,
                "role",
            )
            permission_boundary_with_access = (
                analyze_policies(
                    [permission_boundary],
                    iam,
                    service,
                    permission,
                    "Permission Boundary",
                    role_name,
                    "role",
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
            service_roles[role_name] = list(policies_with_access)

    # Print results
    for role, policies in service_roles.items():
        print(f"\nRole: {role}")
        print("Policies with Access:")
        for policy in policies:
            print(f" - {policy}")

    logging.info(
        "Be advised that this only checks for permissions directly attached to the roles. It does not check for permissions given to groups or users."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find roles with specified service access."
    )
    parser.add_argument(
        "--service", required=True, help="The AWS service to check (e.g., ecs)."
    )
    parser.add_argument(
        "--permissions",
        required=True,
        help="The permissions to check (e.g., CreateCapacityProvider,CreateCluster,CreateService,CreateTaskSet,RegisterContainerInstance,RegisterTaskDefinition,RunTask,StartTask).",
    )
    parser.add_argument("--role", help="Specify a single role to check.")
    args = parser.parse_args()
    main(args.service, args.permissions, args.role)
