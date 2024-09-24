import argparse
import json
import boto3
from datetime import datetime, timedelta

"""
Important: this will look for events under a specific name or ARN, which means that if the secret is being searched for or is being modified or whatever the API call is with the ARN, you need to put that as the name argument.
"""


def query_cloudtrail(secret_name, start_time, end_time):
    client = boto3.client("cloudtrail")
    paginator = client.get_paginator("lookup_events")
    response_iterator = paginator.paginate(
        LookupAttributes=[
            {
                "AttributeKey": "ResourceName",
                "AttributeValue": secret_name,
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
    )

    relevant_events = [
        "CreateSecret",
        "DeleteSecret",
        "PutSecretValue",
        "RestoreSecret",
        "UpdateSecret",
        "PutSecretValue",
    ]

    events = []
    for response in response_iterator:
        for event in response["Events"]:
            event_detail = json.loads(event["CloudTrailEvent"])
            if event_detail["eventName"] in relevant_events:
                events.append(event)
    return events


def format_event(event):
    event_detail = json.loads(event["CloudTrailEvent"])

    return {
        "EventTime": event["EventTime"],
        "Username": event_detail.get("userIdentity", {}).get("userName", "N/A"),
        "ResourceType": event["Resources"][0]["ResourceType"],
        "ResourceName": event["Resources"][0]["ResourceName"],
        "EventName": event_detail["eventName"],
        "SourceIPAddress": event_detail["sourceIPAddress"],
        "UserAgent": event_detail["userAgent"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Query AWS CloudTrail for secret modifications."
    )
    parser.add_argument(
        "secret_name_or_arn", help="The name or ARN of the AWS Secrets Manager secret."
    )
    parser.add_argument(
        "--days",
        type=int,
        required=True,
        help="Number of days back to look for events.",
    )
    args = parser.parse_args()

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=args.days)

    events = query_cloudtrail(args.secret_name_or_arn, start_time, end_time)

    if events:
        formatted_events = [format_event(event) for event in events]
        print(json.dumps(formatted_events, indent=4, default=str))
    else:
        print("No modification events found for the specified secret name or ARN.")

    # Print disclaimer
    print(
        "\nDisclaimer: This script searches for events using the specified secret name or ARN. If the secret is referenced by its ARN in the events, you need to use the ARN as the argument."
    )


if __name__ == "__main__":
    main()
