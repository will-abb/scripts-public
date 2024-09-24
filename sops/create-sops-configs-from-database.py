# -*- coding: utf-8 -*-
import os
import subprocess
import logging
import argparse
import sqlite3


def get_variables_by_repository(db_path, repo_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch repository variables
    cursor.execute(
        "SELECT environment_variable_name, environment_variable_value FROM bitbucket_variables WHERE repository_name = ? AND type = 'repository_variable'",
        (repo_name,),
    )
    repo_vars = cursor.fetchall()

    # Fetch deployment variables
    cursor.execute(
        "SELECT environment_name, environment_variable_name, environment_variable_value FROM bitbucket_variables WHERE repository_name = ? AND type = 'deployment_variable'",
        (repo_name,),
    )
    deploy_vars = cursor.fetchall()

    conn.close()

    return repo_vars, deploy_vars


def create_new_configs_directory(directory_name):
    if os.path.exists(directory_name):
        logging.info(f"Directory '{directory_name}' already exists.")
    else:
        os.makedirs(directory_name)
        logging.info(f"Created new '{directory_name}' directory.")


def write_content_to_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)


def determine_account(env_name):
    env_name_lower = env_name.lower()
    if (
        "production" in env_name_lower
        or "prod" in env_name_lower
        or "-sv" in env_name_lower
        or "east" in env_name_lower
    ):
        return "prod", "586672212047"
    if "uat" in env_name_lower or "release" in env_name_lower:
        return "uat", "463931586000"
    if "development" in env_name_lower or "dev" in env_name_lower:
        return "dev", "690994262422"
    return "dev", "690994262422"


def process_variables(repo_vars, deploy_vars, directory_name, team_name):
    env_vars = {}
    repo_content = ""

    for name, value in repo_vars:
        if value == "SECURED_VALUE":
            repo_content += f"export {name}={value}\n"

    all_env_filename = os.path.join(directory_name, "all-env.enc.env")
    write_content_to_file(all_env_filename, repo_content)

    non_conforming_envs = []
    for env_name, name, value in deploy_vars:
        if value == "SECURED_VALUE":
            if env_name not in env_vars:
                env_vars[env_name] = ""
            env_vars[env_name] += f"export {name}={value}\n"

    sops_commands = []
    for env_name, content in env_vars.items():
        env_key, account_id = determine_account(env_name)
        if "east" in env_name.lower():
            region = "us-east-1"
        else:
            region = "us-west-2"
        env_filename = os.path.join(
            directory_name,
            f"{account_id}-{region}-{env_key}.{team_name}.{env_name.lower()}.enc.env",
        )
        write_content_to_file(env_filename, content)
        sops_commands.append([env_key, env_filename, account_id])

        if not any(
            keyword in env_name.lower()
            for keyword in [
                "production",
                "prod",
                "uat",
                "release",
                "development",
                "dev",
                "-sv",
                "east",
            ]
        ):
            non_conforming_envs.append(env_name)

    if non_conforming_envs:
        print(
            "Some files did not conform to the production, UAT, development naming standards:"
        )
        for env in non_conforming_envs:
            print(f"  - {env}")

    # Add the all-env.enc.env file to the sops_commands list
    sops_commands.append(["prod", all_env_filename, "586672212047"])

    return sops_commands


def create_sops_yaml(directory_name, creation_rules):
    with open(f"{directory_name}/.sops.yaml", "w") as file:
        file.writelines(creation_rules)
    logging.info(f"Created .sops.yaml with rules: {creation_rules}")


def encrypt_files_with_sops(sops_commands, directory_name):
    for aws_short_name, file_path, aws_account_id in sops_commands:
        sops_command = [
            "sops",
            "--config",
            f"{directory_name}/.sops.yaml",
            "-e",
            "-i",
            file_path,
        ]
        os.putenv("AWS_PROFILE", aws_short_name)
        logging.info(f"Encrypting file: {file_path} using profile: {aws_short_name}")
        logging.info(f"Running command: {' '.join(sops_command)}")
        result = subprocess.run(sops_command, capture_output=True, text=True)
        logging.info(f"Command output: {result.stdout}")
        if result.stderr:
            logging.error(f"Command error: {result.stderr}")
        result.check_returncode()


def create_sops_yaml_for_team(directory_name, team_name):
    kms_keys = [
        "AWS-AI-LeadDeveloperAccess",
        "AWS-Finance-LeadDeveloperAccess",
        "AWS-HCSCRM-LeadDeveloperAccess",
        "AWS-HCSservices-LeadDeveloperAccess",
        "AWS-LHA-LeadDeveloperAccess",
        "AWS-LifeCRM-LeadDeveloperAccess",
        "AWS-LifeQuote-LeadDeveloperAccess",
        "AWS-LPDE-LeadDeveloperAccess",
        "AWS-PharmMgmt-LeadDeveloperAccess",
        "AWS-Platform-LeadDeveloperAccess",
        "AWS-Recruiting-LeadDeveloperAccess",
        "AWS-SeniorCRM-LeadDeveloperAccess",
        "AWS-SeniorQuote-LeadDeveloperAccess",
        "AWS-SQAH-LeadDeveloperAccess",
        "AWS-SQT-LeadDeveloperAccess",
        "AWS-SRx-LeadDeveloperAccess",
    ]

    kms_keys = [key for key in kms_keys if team_name.lower() in key.lower()]

    aws_accounts = {690994262422: "dev", 463931586000: "uat", 586672212047: "prod"}

    creation_rules = ["creation_rules:\n"]
    for aws_account_id, aws_short_name in aws_accounts.items():
        for key in kms_keys:
            division = (
                key.replace("LeadDeveloperAccess", "")
                .replace("AWS", "")
                .replace("-", "")
            )
            creation_rules.append(
                f"  - path_regex: .*{aws_account_id}-us-west-2-{aws_short_name}\.{team_name}\..*\.enc\.env$\n"
                f'    kms: "arn:aws:kms:us-west-2:{aws_account_id}:alias/{key},arn:aws:kms:us-east-1:{aws_account_id}:alias/{key}"\n'
            )

    # Rule for all-env.enc.env file
    prod_key = kms_keys[0]
    creation_rules.append(
        f'  - path_regex: .*all-env.enc.env$\n    kms: "arn:aws:kms:us-west-2:586672212047:alias/{prod_key},arn:aws:kms:us-east-1:586672212047:alias/{prod_key}"\n'
    )

    create_sops_yaml(directory_name, creation_rules)


def main():
    parser = argparse.ArgumentParser(
        description="Extract variables, create config files, and encrypt them with SOPS."
    )
    parser.add_argument(
        "--db", required=True, help="Path to the Bitbucket variables database."
    )
    parser.add_argument("--repo", required=True, help="Repository name.")
    parser.add_argument(
        "--team", required=True, help="Specify a team or role to filter."
    )
    args = parser.parse_args()

    directory_name = "sops-configs"
    create_new_configs_directory(directory_name)

    repo_vars, deploy_vars = get_variables_by_repository(args.db, args.repo)
    sops_commands = process_variables(repo_vars, deploy_vars, directory_name, args.team)

    create_sops_yaml_for_team(directory_name, args.team)

    encrypt_files_with_sops(sops_commands, directory_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
