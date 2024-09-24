import boto3
import argparse


def list_iam_users(limit, order):
    """
    List IAM users in the specified order up to the given limit.
    """
    client = boto3.client("iam")
    paginator = client.get_paginator("list_users")
    # Sorting IAM users based on the CreationDate in the specified order
    response = paginator.paginate(PaginationConfig={"MaxItems": limit})
    users = []
    for page in response:
        for user in page["Users"]:
            users.append(user)

    # Sorting users by 'CreateDate' in the specified order
    users_sorted = sorted(
        users, key=lambda x: x["CreateDate"], reverse=(order == "desc")
    )

    for user in users_sorted:
        print(
            f"User: {user['UserName']}, Created At: {user['CreateDate']}, Arn: {user['Arn']}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List a specified number of IAM users in a specified order."
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="The number of IAM users to list."
    )
    parser.add_argument(
        "--order",
        type=str,
        choices=["asc", "desc"],
        default="asc",
        help="Order to list the IAM users by creation date (ascending or descending).",
    )
    args = parser.parse_args()

    list_iam_users(args.limit, args.order)
