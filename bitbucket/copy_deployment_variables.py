import argparse
import json
import os
import urllib.parse

import requests


def get_auth_headers(token):
    """Construct authorization headers for the request."""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


def get_environment_uuid(base_url, token, owner, repo_slug, environment_name):
    """Retrieve UUID for a given environment name."""
    url = f"{base_url}/repositories/{owner}/{repo_slug}/environments/"
    headers = get_auth_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    environments = response.json()["values"]
    for env in environments:
        if env["name"] == environment_name:
            return env["uuid"]
    raise ValueError(f"Environment '{environment_name}' not found.")


def get_deployment_variables(base_url, token, owner, repo_slug, environment_uuid):
    """Get deployment variables for a given environment UUID."""
    url = f"{base_url}/repositories/{owner}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables"
    headers = get_auth_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["values"]


def create_deployment_variable(
    base_url, token, owner, repo_slug, variable, environment_uuid
):
    """Create a deployment variable in the target environment."""
    decoded_uuid = urllib.parse.unquote(
        environment_uuid
    )  # Ensure the UUID is not URL-encoded
    url = f"{base_url}/repositories/{owner}/{repo_slug}/deployments_config/environments/{decoded_uuid}/variables"
    payload = json.dumps(variable)
    headers = get_auth_headers(token)
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def create_deployment_environment(
    base_url, token, owner, repo_slug, name, environment_type
):
    """Create a new deployment environment with the given name and type."""
    url = f"{base_url}/repositories/{owner}/{repo_slug}/environments"
    payload = json.dumps(
        {
            "type": "deployment_environment",
            "name": name,
            "environment_type": {
                "name": environment_type,
                "type": "deployment_environment_type",
            },
        }
    )
    headers = get_auth_headers(token)
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Error creating environment: {response.text}")
    return response.json().get("uuid")


def list_environment_variables(base_url, token, owner, repo_slug, environment_name):
    """Print the deployment variables for a given environment."""
    environment_uuid = get_environment_uuid(
        base_url, token, owner, repo_slug, environment_name
    )
    variables = get_deployment_variables(
        base_url, token, owner, repo_slug, environment_uuid
    )
    for variable in variables:
        secret_indicator = "SECRET" if variable["secured"] else "not secret"
        print(f"{variable['key']} (secured: {secret_indicator})")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Manage Bitbucket deployment environments."
    )
    parser.add_argument(
        "--source-env-name", required=True, help="Name of the source environment."
    )
    parser.add_argument(
        "--target-env-name", help="Name of the target environment to create."
    )
    parser.add_argument(
        "--target-env-type",
        help="Type of the target environment (e.g., test, staging, production).",
    )
    parser.add_argument(
        "--repo-slug", required=True, help="Slug of the Bitbucket source repository."
    )
    parser.add_argument(
        "--repo-owner",
        required=False,
        default="selectquote",
        help="Owner of the Bitbucket source repository. Default: 'selectquote'",
    )
    parser.add_argument(
        "--target-repo-slug",
        required=True,
        help="Slug of the Bitbucket target repository.",
    )
    parser.add_argument(
        "--target-repo-owner",
        required=False,
        default="selectquote",
        help="Owner of the Bitbucket target repository.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List variables from the source environment.",
    )
    return parser.parse_args()


def ensure_bitbucket_token():
    """Ensure that the Bitbucket token is available."""
    token = os.environ.get("BITBUCKET_API_TOKEN")
    if not token:
        raise OSError("BITBUCKET_API_TOKEN environment variable is not set.")
    return token


def copy_variables_to_new_environment(base_url, token, args):
    """Copy variables from the source to the new target environment."""
    uuid = create_deployment_environment(
        base_url,
        token,
        args.target_repo_owner,
        args.target_repo_slug,
        args.target_env_name,
        args.target_env_type,
    )
    print(f"New environment '{args.target_env_name}' created with UUID: {uuid}")
    source_uuid = get_environment_uuid(
        base_url, token, args.repo_owner, args.repo_slug, args.source_env_name
    )
    variables = get_deployment_variables(
        base_url, token, args.repo_owner, args.repo_slug, source_uuid
    )
    for variable in variables:
        secret_text = (
            "as a SECRET. Please update its value manually."
            if variable["secured"]
            else "with value: " + variable["value"]
        )
        print(
            f"Variable '{variable['key']}' copied to the new environment {secret_text}"
        )
        if variable["secured"]:
            variable["value"] = "secret"  # Use a placeholder for secret variables
        create_deployment_variable(
            base_url,
            token,
            args.target_repo_owner,
            args.target_repo_slug,
            variable,
            uuid,
        )


def main():
    args = parse_arguments()
    token = ensure_bitbucket_token()
    base_url = "https://api.bitbucket.org/2.0"

    if args.list:
        list_environment_variables(
            base_url, token, args.repo_owner, args.repo_slug, args.source_env_name
        )
    elif args.target_env_name and args.target_env_type:
        copy_variables_to_new_environment(base_url, token, args)
    else:
        raise ValueError("Both target environment name and type must be specified.")


if __name__ == "__main__":
    main()
