import argparse
import logging
import boto3
from iam_utils import (
    get_groups,
    get_managed_policies,
    get_inline_policies,
    get_permission_boundaries,
    analyze_policies,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Main function
def main(service, permissions, single_group=None):
    iam = boto3.client("iam")

    # Split permissions into a list
    permissions_list = permissions.split(",")

    # Retrieve groups
    groups = [single_group] if single_group else get_groups()
    # logging.info(f"Groups to be checked: {groups}")

    service_groups = {}

    # Analyze group policies
    for group_name in groups:
        # logging.info(f"Analyzing policies for group: {group_name}")

        managed_policies = get_managed_policies(group_name, "group")
        # logging.info(f"Managed policies for {group_name}: {managed_policies}")

        inline_policies = get_inline_policies(group_name, "group")
        # logging.info(f"Inline policies for {group_name}: {inline_policies}")

        permission_boundary = get_permission_boundaries(group_name, "group")
        # logging.info(f"Permission boundary for {group_name}: {permission_boundary}")

        policies_with_access = set()

        for permission in permissions_list:
            managed_policies_with_access = analyze_policies(
                managed_policies,
                iam,
                service,
                permission,
                "Managed Policy",
                group_name,
                "group",
            )
            inline_policies_with_access = analyze_policies(
                inline_policies,
                iam,
                service,
                permission,
                "Inline Policy",
                group_name,
                "group",
            )
            permission_boundary_with_access = (
                analyze_policies(
                    [permission_boundary],
                    iam,
                    service,
                    permission,
                    "Permission Boundary",
                    group_name,
                    "group",
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
            service_groups[group_name] = list(policies_with_access)

    # Print results
    for group, policies in service_groups.items():
        print(f"\nGroup: {group}")
        print("Policies with Access:")
        for policy in policies:
            print(f" - {policy}")

    logging.info(
        "Be advised that this only checks for permissions directly attached to the group. It does not check for permissions given through roles or permissions directly attached to users."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find groups with specified service access."
    )
    parser.add_argument(
        "--service", required=True, help="The AWS service to check (e.g., ecs)."
    )
    parser.add_argument(
        "--permissions",
        required=True,
        help="The permissions to check (e.g., RegisterTaskDefinition,RunTask,StartTask).",
    )
    parser.add_argument("--group", help="Specify a single group to check.")
    args = parser.parse_args()
    main(args.service, args.permissions, args.group)
