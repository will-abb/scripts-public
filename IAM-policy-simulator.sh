#!/bin/bash

roles=(
    "aws-elasticbeanstalk-ec2-role"
    "aws-elasticbeanstalk-service-role"
    "AWSServiceRoleForElasticBeanstalkManagedUpdates"
    "copilot-instance"
    "cost-optimizer-for-amazon-worksp-InvokeECSTaskRole-1I6P071D39C05"
    "datadog-agent-ecs"
    "ecsCodeDeployRole"
    "ecsEventsRole"
    "ecsInstanceDevOpsRole"
    "ecsInstanceRole"
    "RestartECSService"
    "SQ-Load-Test-Prod-DLTApiDLTAPIServicesLambdaRole44-MTTP2CQ70ONA"
    "SQ-Load-Test-Prod-DLTLambdaFunctionDLTTestLambdaTa-1DJFW6WT27ES"
    "SRTS-srts2-life-match-manager-st-cw-role"
    "TransactionTransformationAlertLambdaRole"
)
action_name="ecs:TagResource"

for role in "${roles[@]}"; do
    policy_arn="arn:aws:iam::$(aws sts get-caller-identity --query 'Account' --output text):role/${role}"
    
    echo "Checking role: $role"
    
    result=$(aws iam simulate-principal-policy \
        --policy-source-arn "$policy_arn" \
        --action-names "$action_name" \
        --output text)
    
    decision=$(echo "$result" | awk '/ecs:TagResource/ {print $3}')
    
    if [ "$decision" == "allowed" ]; then
        status="Allowed"
    else
        status="Denied"
    fi
    
    echo "Role: $role - Action: $action_name - Result: $status"
done
