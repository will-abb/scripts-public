# Bitbucket Deployment Environment Script

## Overview
This script automates the process of copying deployment variables from one environment to another within Bitbucket. Now, it also supports copying variables between different repositories, helping to avoid manual errors and simplify the setup of new ECS services in BitBucket. It can list variables from a source environment and create a new deployment environment with copied variables in the same or a different repository.

## Prerequisites
To use this script, you must have a Bitbucket workspace access token with the following permissions:
- `pipeline`
- `pipeline:variable`
- `pipeline:write`
- `project`
- `repository`
- `repository:admin`
- `repository:write`
These scopes are necessary for the script to interact with the Bitbucket API for various operations related to deployment environments.

**you must export bitbucket token first:**
``` shell
export BITBUCKET_API_TOKEN=your_token_here
```

## Usage
1. **List Variables:**
   Lists all variables from the specified source environment.
   ```shell
   python3 copy-deployment-variables.py --source-env-name "<source-environment>" --repo-slug "<source-repository-slug>" --repo-owner "<source-repository-owner>" --list
   ```

2. **Copy Variables to a New Environment in the Same or Different Repository:**
   Copies all variables from the source environment to a newly created target environment in the specified repository.
   ```shell
   python3 copy-deployment-variables.py --source-env-name "<source-environment>" --target-env-name "<target-environment>" --target-env-type "<environment-type>" --repo-slug "<source-repository-slug>" --repo-owner "<source-repository-owner>" --target-repo-slug "<target-repository-slug>" --target-repo-owner "<target-repository-owner>"
   ```
   Note: `environment_type` should be one of 'test', 'staging', or 'production'.

3. **Example:**
   Create a new bitbucket deployment environment of type `test` called `development-lha` in the `socket-server-automations` repository and copy the variables of the already existing deployment environment `development` from the `acd-api` repository.
   ```shell
   python3 copy_deployment_variables.py  --source-env-name uat-senior --repo-slug acd-api --target-repo-slug acd-api --target-env-name uat-life --target-env-type staging
   ```

## Secret Variables
The script copies secret variables as placeholders with the value 'secret' since it cannot access actual secret values from Bitbucket. After running the script, you'll need to manually update secret variables in the target environment with the correct values.

## Troubleshooting
- **Environment Not Found:**
  Ensure the source environment name is correct and exists in your Bitbucket repository.

- **Invalid Permissions:**
  Verify that your Bitbucket access token has the correct scopes as listed in the prerequisites.

- **Duplicate Environment Name:**
  If the target environment name already exists, use a unique name for the new environment.

- **403 Forbidden Error:**
  This typically indicates a scope issue. Make sure your access token includes all the required permissions.
