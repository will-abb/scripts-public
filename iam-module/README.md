# IAM Permissions Checker

This repository contains scripts to check IAM policies for users, groups, and roles in AWS. These scripts can be used to verify the permissions granted to IAM entities either individually or collectively. The `iam_utils.py` module contains the core logic for fetching and analyzing IAM policies.

## Files

- `check-user-permissions.py`: Script to check the IAM policies for a specific user or all users.
- `check-group-permissions.py`: Script to check the IAM policies for a specific group or all groups.
- `check-role-permissions.py`: Script to check the IAM policies for a specific role or all roles.
- `iam_utils.py`: Module containing utility functions for fetching and analyzing IAM policies.

## Usage

### Check User Permissions

This script checks the IAM policies for a specific user or all users. It requires the AWS service and permissions to check as arguments.

#### Example: Check permissions for a specific user

```sh
python3 check-user-permissions.py --service <service> --permissions <permissions> --user <username>
```

#### Example: Check permissions for all users

```sh
python3 check-user-permissions.py --service <service> --permissions <permissions>
```

### Check Group Permissions

This script checks the IAM policies for a specific group or all groups. It requires the AWS service and permissions to check as arguments.

#### Example: Check permissions for a specific group

```sh
python3 check-group-permissions.py --service <service> --permissions <permissions> --group <groupname>
```

#### Example: Check permissions for all groups

```sh
python3 check-group-permissions.py --service <service> --permissions <permissions>
```

### Check Role Permissions

This script checks the IAM policies for a specific role or all roles. It requires the AWS service and permissions to check as arguments.

#### Example: Check permissions for a specific role

```sh
python3 check-role-permissions.py --service <service> --permissions <permissions> --role <rolename>
```

#### Example: Check permissions for all roles

```sh
python3 check-role-permissions.py --service <service> --permissions <permissions>
```

## IAM Utils

The `iam_utils.py` module contains utility functions for fetching and analyzing IAM policies. This module is imported and used by the other scripts to perform the core logic of checking and gathering policies.

### Logic Overview

1. **Fetching IAM Entities**: Functions like `get_users`, `get_groups`, and `get_roles` are used to fetch the list of IAM users, groups, and roles respectively.

2. **Fetching Policies**: 
    - **Managed Policies**: The `get_managed_policies` function retrieves the managed policies attached to the IAM entity.
    - **Inline Policies**: The `get_inline_policies` function retrieves the inline policies attached to the IAM entity.
    - **Permission Boundaries**: The `get_permission_boundaries` function retrieves the permission boundaries attached to the IAM entity (applicable only for users and roles).

3. **Analyzing Policies**:
    - The `analyze_policies` function is responsible for analyzing both managed and inline policies to determine if they grant the specified service and permissions.
    - It calls the `has_service_access` function which checks for various types of permissions:
        - **Full Admin Access**: Checks if the policy grants full admin access using wildcards like `*:*` or `*`.
        - **Service Admin Access**: Checks if the policy grants admin access to the specified service (e.g., `ec2:*`).
        - **Exact Permission Match**: Checks if the policy grants the exact specified permission (e.g., `ec2:RunInstances`).
        - **Wildcard Permission Match**: Checks if the policy grants the permission using wildcards (e.g., `ec2:Get*`).

4. **Wildcard Checks**:
    - The logic emphasizes the ability to perform wildcard checks to ensure comprehensive permission analysis. This means that not only exact matches are considered but also wildcard patterns that might grant broader access than intended.

## Setup

Before running the scripts, make sure you have the required dependencies installed. You can install the dependencies using `pip`:

```sh
pip install boto3
```

