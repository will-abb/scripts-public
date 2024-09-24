import boto3
import argparse
import re
import json
from datetime import datetime, timedelta


def get_cloudtrail_events(event_name, start_time, end_time):
    client = boto3.client("cloudtrail")
    response = client.lookup_events(
        LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": event_name}],
        StartTime=start_time,
        EndTime=end_time,
    )
    return response


def filter_events_by_resource_name(events, resource_name_pattern):
    regex = re.compile(resource_name_pattern)
    filtered_events = []

    for event in events["Events"]:
        for resource in event["Resources"]:
            if regex.search(resource["ResourceName"]):
                filtered_events.append(event)
                break

    return filtered_events


def format_event_time(event_time):
    return event_time.strftime("%Y-%m-%d %H:%M:%S %Z")


def print_event_summary(events):
    for event in events:
        cloudtrail_event = json.loads(event.get("CloudTrailEvent", "{}"))
        role_arn = cloudtrail_event.get("userIdentity", {}).get("arn", "N/A")

        event_summary = {
            "EventName": event.get("EventName"),
            "AccessKeyId": event.get("AccessKeyId"),
            "Username": event.get("Username"),
            "EventTime": format_event_time(event.get("EventTime")),
            "ResourceName": event["Resources"][0].get("ResourceName")
            if event.get("Resources")
            else "N/A",
            "RoleArn": role_arn,
        }

        for key, value in event_summary.items():
            print(f"{key}: {value}")
        print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch CloudTrail events for a specified event name and number of days, filtering by resource name."
    )
    parser.add_argument(
        "--event-name",
        type=str,
        required=True,
        help="The name of the event to filter by.",
    )
    parser.add_argument(
        "--days",
        type=int,
        required=True,
        help="Number of days to look back from today.",
    )
    parser.add_argument(
        "--resource-name-pattern",
        type=str,
        required=True,
        help="Regular expression pattern to filter resource names.",
    )

    args = parser.parse_args()
    event_name = args.event_name
    days = args.days
    resource_name_pattern = args.resource_name_pattern

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    events = get_cloudtrail_events(event_name, start_time, end_time)
    filtered_events = filter_events_by_resource_name(events, resource_name_pattern)

    print_event_summary(filtered_events)


if __name__ == "__main__":
    main()
