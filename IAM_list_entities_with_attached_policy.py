import boto3
import argparse


def list_entities_with_policy(policy_arn):
    iam = boto3.client("iam")

    entities = {"User": [], "Role": [], "Group": []}

    def get_entities(entity_type, policy_arn):
        paginator = iam.get_paginator("list_entities_for_policy")
        for response in paginator.paginate(
            PolicyArn=policy_arn, EntityFilter=entity_type
        ):
            for entity in response[f"Policy{entity_type}s"]:
                entities[entity_type].append(entity[f"{entity_type}Name"])

    for entity_type in entities.keys():
        get_entities(entity_type, policy_arn)

    return entities


def main():
    parser = argparse.ArgumentParser(
        description="List all IAM entities with a specified policy attached."
    )
    parser.add_argument(
        "--policy-arn", type=str, help="The ARN of the policy to check."
    )
    args = parser.parse_args()

    attached_entities = list_entities_with_policy(args.policy_arn)

    for entity_type, names in attached_entities.items():
        if names:  # Only print if there are names in the list
            print(f"{entity_type}s with '{args.policy_arn}' policy attached:")
            for name in names:
                print(f"- {name}")
        else:
            print(f"No {entity_type}s have '{args.policy_arn}' policy attached.")


if __name__ == "__main__":
    main()
