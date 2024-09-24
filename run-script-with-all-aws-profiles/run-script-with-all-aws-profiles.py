import os
import boto3
import subprocess
import argparse
import shutil

# I think the inner script arguments (not this script's) have to be at the end. modify account list at the end of script. see
# readme for more info
# python run_script_with_all_aws_profiles.py --include-east IAM_list_iam_users.py --script-args --limit 3 --order desc


def print_divider():
    """
    Print a divider line of hash signs based on the terminal width.
    """
    terminal_width = shutil.get_terminal_size().columns
    print("#" * terminal_width)


def get_account_details(profile):
    """
    Retrieve the account alias and account ID using the specified profile.
    """
    session = boto3.Session(profile_name=profile)
    client = session.client("sts")
    account_id = client.get_caller_identity().get("Account")

    iam_client = session.client("iam")
    try:
        aliases = iam_client.list_account_aliases()["AccountAliases"]
        account_alias = aliases[0] if aliases else "No alias found"
    except Exception as e:
        print(f"Error retrieving account alias for profile {profile}: {e}")
        account_alias = "Error retrieving alias"

    return account_alias, account_id


def confirm_and_execute(script_name, profile, script_args, no_verify):
    """
    Ask for user confirmation before executing the specified script with the given profile.
    """
    account_alias, account_id = get_account_details(profile)
    print(
        f"Profile: {profile}, Account Name (Alias): {account_alias}, Account ID: {account_id}"
    )

    if no_verify:
        response = "y"
        print("Running without verification due to --no-verify option.")
    else:
        response = input(
            f"The command will be run by the following profile: {profile}. Are you sure you want to do this? (Y/N): "
        )

    if response.lower() in ["y", "yes"]:
        os.environ["AWS_PROFILE"] = profile
        os.environ["AWS_DEFAULT_REGION"] = boto3.Session(
            profile_name=profile
        ).region_name
        script_args = script_args if script_args is not None else []
        command = f"python {script_name} {' '.join(script_args)}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    elif response.lower() in ["n", "no"]:
        quit_response = input("Do you want to quit the script? (Y/N): ")
        if quit_response.lower() in ["y", "yes"]:
            print("Exiting the script.")
            exit()
        else:
            print("Continuing with the next profile...")
    print_divider()


def main(script_name, include_east, no_verify, script_args):
    """
    Run the specified script for each profile after retrieving account details and user confirmation.
    """
    # modify list as needed
    profiles = [
        "audit",
        "audit-east",
        "aws-management-read",
        "aws-management-read-east",
        "data-science-read",
        "data-science-read-east",
        "dev-read",
        "dev-read-east",
        "devops-read",
        "devops-read-east",
        "finance",
        "finance-east",
        "healthcareservices-read",
        "healthcareservices-read-east",
        "inside-response-read",
        "inside-response-read-east",
        "log-archive",
        "log-archive-east",
        "marketing-read",
        "marketing-read-east",
        "paid-social-read",
        "paid-social-read-east",
        "play-read",
        "play-read-east",
        "prod-read",
        "prod-read-east",
        "propulsions-read",
        "propulsions-read-east",
        "security-compliance-read",
        "security-compliance-read-east",
        "shared-services-read",
        "shared-services-read-east",
        "sox-read",
        "sox-read-east",
        "telecom-read",
        "telecom-read-east",
        "uat-read",
        "uat-read-east",
        "selectquote-network-read",
        "selectquote-network-read-east",
    ]

    if include_east:
        filtered_profiles = profiles
    else:
        filtered_profiles = [profile for profile in profiles if "-east" not in profile]

    for profile in filtered_profiles:
        confirm_and_execute(script_name, profile, script_args, no_verify)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a script for each provided AWS profile with optional user confirmation."
    )
    parser.add_argument("script_name", help="The name of the script to run.")
    parser.add_argument(
        "--include-east",
        action="store_true",
        help="Include profiles ending with '-east' when running the script.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Run the script for each profile without verification.",
    )
    parser.add_argument(
        "--script-args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to the script being executed.",
    )
    args = parser.parse_args()

    main(args.script_name, args.include_east, args.no_verify, args.script_args)
