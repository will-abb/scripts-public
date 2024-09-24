import boto3
import argparse


def get_alb_subnets(alb_name):
    elbv2 = boto3.client("elbv2")
    response = elbv2.describe_load_balancers(Names=[alb_name])
    subnets = [
        az["SubnetId"] for az in response["LoadBalancers"][0]["AvailabilityZones"]
    ]
    return subnets


def is_public_subnet(subnet_id):
    ec2 = boto3.client("ec2")
    response = ec2.describe_route_tables(
        Filters=[{"Name": "association.subnet-id", "Values": [subnet_id]}]
    )
    for route_table in response["RouteTables"]:
        for route in route_table["Routes"]:
            if (
                route.get("DestinationCidrBlock") == "0.0.0.0/0"
                and "GatewayId" in route
                and route["GatewayId"].startswith("igw")
            ):
                return True
    return False


def get_target_group_arn(cluster_name, service_name):
    ecs = boto3.client("ecs")
    response = ecs.describe_services(cluster=cluster_name, services=[service_name])
    if not response["services"]:
        print(
            f"No ECS service found with the name {service_name} in cluster {cluster_name}."
        )
        return None
    service = response["services"][0]
    for lb in service.get("loadBalancers", []):
        return lb["targetGroupArn"]
    print(
        f"No target group found for ECS service {service_name} in cluster {cluster_name}."
    )
    return None


def get_target_group_name(target_group_arn):
    elbv2 = boto3.client("elbv2")
    response = elbv2.describe_target_groups(TargetGroupArns=[target_group_arn])
    if not response["TargetGroups"]:
        print(f"No target group found with ARN {target_group_arn}.")
        return None
    return response["TargetGroups"][0]["TargetGroupName"]


def get_alb_from_target_group(target_group_arn):
    elbv2 = boto3.client("elbv2")
    response = elbv2.describe_target_groups(TargetGroupArns=[target_group_arn])
    if not response["TargetGroups"]:
        print(f"No target group found with ARN {target_group_arn}.")
        return None
    load_balancer_arn = response["TargetGroups"][0]["LoadBalancerArns"][0]
    response = elbv2.describe_load_balancers(LoadBalancerArns=[load_balancer_arn])
    if not response["LoadBalancers"]:
        print(f"No load balancer found with ARN {load_balancer_arn}.")
        return None
    return response["LoadBalancers"][0]["LoadBalancerName"]


def check_alb_visibility(alb_name):
    subnets = get_alb_subnets(alb_name)
    for subnet_id in subnets:
        if is_public_subnet(subnet_id):
            return "public"
    return "private"


def check_service_visibility(cluster_name, service_name):
    target_group_arn = get_target_group_arn(cluster_name, service_name)
    if not target_group_arn:
        return
    target_group_name = get_target_group_name(target_group_arn)
    alb_name = get_alb_from_target_group(target_group_arn)
    if not alb_name:
        return
    alb_visibility = check_alb_visibility(alb_name)
    print(f"Service {service_name} is {alb_visibility}.")
    print(
        f"It is part of cluster {cluster_name} and belongs to target group {target_group_name}."
    )
    print(f"Load balancer {alb_name} is {alb_visibility}.")


def main(alb_name=None, cluster_name=None, service_name=None):
    if alb_name:
        alb_visibility = check_alb_visibility(alb_name)
        print(f"Load balancer {alb_name} is {alb_visibility}.")
    elif cluster_name and service_name:
        check_service_visibility(cluster_name, service_name)
    else:
        print(
            "Either --alb-name or both --cluster-name and --service-name must be provided."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if an AWS ALB or ECS service is public or private."
    )
    parser.add_argument("--alb-name", help="The name of the ALB.")
    parser.add_argument("--cluster-name", help="The name of the ECS cluster.")
    parser.add_argument("--service-name", help="The name of the ECS service.")
    args = parser.parse_args()
    main(args.alb_name, args.cluster_name, args.service_name)
