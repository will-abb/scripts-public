import boto3
import argparse
from datetime import datetime


def get_all_clusters():
    client = boto3.client("ecs")
    paginator = client.get_paginator("list_clusters")
    cluster_arns = []
    for page in paginator.paginate():
        cluster_arns.extend(page["clusterArns"])
    return cluster_arns


def get_all_services(cluster_name):
    client = boto3.client("ecs")
    paginator = client.get_paginator("list_services")
    service_arns = []
    for page in paginator.paginate(cluster=cluster_name):
        service_arns.extend(page["serviceArns"])
    return service_arns


def get_deployments(cluster_name, service_name):
    client = boto3.client("ecs")
    response = client.describe_services(cluster=cluster_name, services=[service_name])

    deployments = response["services"][0]["deployments"]
    return deployments


def calculate_durations(deployments):
    deployment_durations = []
    for deployment in deployments:
        if "createdAt" in deployment and "updatedAt" in deployment:
            start_time = deployment["createdAt"]
            end_time = deployment["updatedAt"]
            duration = end_time - start_time
            status = deployment["status"]
            deployment_durations.append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": status,
                }
            )
    return deployment_durations


def main(cluster_name, service_name, verbose):
    if cluster_name == "ALL":
        clusters = get_all_clusters()
    else:
        clusters = [cluster_name]

    for cluster in clusters:
        if service_name == "ALL":
            services = get_all_services(cluster)
        else:
            services = [service_name]

        for service in services:
            service_name_only = service.split("/")[-1]
            try:
                deployments = get_deployments(cluster, service)
                durations = calculate_durations(deployments)
                if verbose:
                    print(f"Cluster: {cluster}, Service: {service}")
                else:
                    print(f"Cluster: {cluster}, Service: {service_name_only}")
                for d in durations:
                    if verbose:
                        print(
                            "Start Time: {}, End Time: {}, Duration: {}, Status: {}".format(
                                d["start_time"],
                                d["end_time"],
                                d["duration"],
                                d["status"],
                            )
                        )
                    else:
                        print(f"Duration: {d['duration']}")
            except Exception as e:
                print(
                    f"Error retrieving deployments for cluster '{cluster}' and service '{service_name_only}': {e}"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get ECS deployment durations.")
    parser.add_argument(
        "--cluster-name", required=True, help="Name of the ECS cluster or 'ALL'"
    )
    parser.add_argument(
        "--service-name", required=True, help="Name of the ECS service or 'ALL'"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Display detailed output"
    )

    args = parser.parse_args()
    main(args.cluster_name, args.service_name, args.verbose)
