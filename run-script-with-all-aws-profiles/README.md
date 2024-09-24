# run-script-with-all-aws-profiles.py

## Overview

This script is designed to run a specified script across multiple AWS profiles. It retrieves account details, optionally verifies user confirmation, and executes the script with the provided arguments for each profile.

## How It Works

- Retrieves AWS account details (alias and account ID) using the specified profile.
- Optionally asks for user confirmation before executing the script for each profile.
- Executes the specified script with the given arguments for each profile.
- **It's very important that you update the profiles list at the very bottom of the script to your needs.**

## Usage

### Command Structure

```sh
python3 run-script-with-all-aws-profiles.py <script_name> [options] --script-args <args_for_secondary_script>
```

### Options

- `script_name`: The name of the script to run for each profile.
- `--include-east`: Include profiles ending with '-east' when running the script.
- `--no-verify`: Run the script for each profile without user verification.
- `--script-args`: Additional arguments to pass to the secondary script being executed.

### Examples

#### Basic Example

To run `check-user-permissions.py` with arguments for ECS permissions:

```sh
python3 run-script-with-all-aws-profiles.py check-user-permissions.py --script-args --service ecs --permissions CreateCapacityProvider,CreateCluster,CreateService,CreateTaskSet,RegisterContainerInstance,RegisterTaskDefinition,RunTask,StartTask
```

#### Including East Profiles

To include profiles ending with '-east':

```sh
python3 run-script-with-all-aws-profiles.py check-user-permissions.py --include-east --script-args --service ecs --permissions CreateCapacityProvider,CreateCluster,CreateService,CreateTaskSet,RegisterContainerInstance,RegisterTaskDefinition,RunTask,StartTask
```

#### Running Without Verification

To run without user verification:

```sh
python3 run-script-with-all-aws-profiles.py check-user-permissions.py --no-verify --script-args --service ecs --permissions CreateCapacityProvider,CreateCluster,CreateService,CreateTaskSet,RegisterContainerInstance,RegisterTaskDefinition,RunTask,StartTask
```

### Notes

- Ensure you have AWS CLI and `boto3` installed and configured.
- The profiles list in the script should be updated with your AWS profiles.
