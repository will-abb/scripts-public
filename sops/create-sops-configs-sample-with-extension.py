# -*- coding: utf-8 -*-
import os
import subprocess
import logging
import argparse


def encrypted_file_exists(filename):
    if not os.path.exists(filename):
        return False

    with open(filename, "r") as file:
        lines = file.read()
        if "ENC[AES256" in lines:
            return True
        else:
            return False


def create_new_configs_directory(directory_name):
    if os.path.exists(directory_name):
        logging.info(f"Directory '{directory_name}' already exists.")
    else:
        os.makedirs(directory_name)
        logging.info(f"Created new '{directory_name}' directory.")


def write_content_to_file(filename, key, aws_account_id, aws_short_name, file_format):
    if file_format == "yaml":
        content = f"hello: {key} in AWS Account {aws_account_id} ({aws_short_name})\n"
    elif file_format == "json":
        content = (
            f'{{"hello": "{key} in AWS Account {aws_account_id} ({aws_short_name})"}}\n'
        )
    elif file_format == "env":
        content = (
            f"export HELLO={key} in AWS Account {aws_account_id} ({aws_short_name})\n"
        )
    else:
        content = f"Hello {key} in AWS Account {aws_account_id} ({aws_short_name})\n"

    with open(filename, "w") as file:
        file.write(content)


def create_sops_yaml(directory_name, creation_rules):
    with open(f"{directory_name}/.sops.yaml", "w") as file:
        file.writelines(creation_rules)


def encrypt_files_with_sops(sops_commands, directory_name):
    for aws_short_name, filename, aws_account_id in sops_commands:
        sops_command = [
            "sops",
            "--config",
            f"{directory_name}/.sops.yaml",
            "-e",
            "-i",
            f"{filename}",
        ]
        os.putenv("AWS_PROFILE", aws_short_name)
        logging.info(f"{sops_command}")
        subprocess.run(sops_command)


if __name__ == "__main__":
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

    valid_formats = ["txt", "json", "yaml", "env"]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--team", help="Specify a team or role to filter", required=False
    )
    parser.add_argument(
        "--format",
        help="Specify the file format (txt, json, yaml, env)",
        required=False,
        choices=valid_formats,
        default="env",
    )
    args = parser.parse_args()

    if args.team and args.team.lower() == "all":
        directory_name = "newly-generated-configs-all"
        team = None
    elif args.team:
        directory_name = f"newly-generated-configs-{args.team}"
        team = args.team.lower()
        kms_keys = [key for key in kms_keys if team in key.lower()]
    else:
        directory_name = "newly-generated-configs-all"

    create_new_configs_directory(directory_name)

    if os.environ.get("DEBUG"):
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level)

    aws_accounts = {690994262422: "dev", 463931586000: "uat", 586672212047: "prod"}
    creation_rules = ["creation_rules:\n"]

    sops_commands = []

    for aws_account_id, aws_short_name in aws_accounts.items():
        for key in kms_keys:
            division = key.replace("LeadDeveloperAccess", "").replace("AWS", "")
            filename = f"{directory_name}/{aws_account_id}-us-west-2-{aws_short_name}.{division.lower()}.enc.{args.format}"
            creation_rules.append(
                f'  - path_regex: .*.{aws_short_name}.{division.lower()}.enc.*$\n    kms: "arn:aws:kms:us-west-2:{aws_account_id}:alias/{key},arn:aws:kms:us-east-1:{aws_account_id}:alias/{key}"\n'
            )
            if not encrypted_file_exists(filename):
                write_content_to_file(
                    filename, key, aws_account_id, aws_short_name, args.format
                )
                sops_commands.append([aws_short_name, filename, aws_account_id])
            else:
                logging.info(
                    f"{filename} already exists and is encrypted, nothing to do here."
                )

    # Create and encrypt the additional file with production keys
    if args.team and args.team.lower() != "all":
        all_env_filename = f"{directory_name}/all-env.enc.{args.format}"
        prod_key = kms_keys[
            0
        ]  # Assuming the first key in the filtered list is the production key for the team
        write_content_to_file(
            all_env_filename, prod_key, 586672212047, "prod", args.format
        )
        sops_commands.append(["prod", all_env_filename, 586672212047])
        creation_rules.append(
            f'  - path_regex: .*all-env.enc.*$\n    kms: "arn:aws:kms:us-west-2:586672212047:alias/{prod_key},arn:aws:kms:us-east-1:586672212047:alias/{prod_key}"\n'
        )

    # Write .sops.yaml only in the newly created configs directory
    create_sops_yaml(directory_name, creation_rules)

    # Encrypt files using the newly created .sops.yaml
    encrypt_files_with_sops(sops_commands, directory_name)
