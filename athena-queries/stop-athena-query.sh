#!/bin/bash

# Ensure a QueryExecutionId is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <query-execution-id>"
    exit 1
fi

QUERY_EXECUTION_ID=$1

# Define the region
REGION="us-east-2"

# Stop the Athena query
aws athena stop-query-execution \
    --query-execution-id "$QUERY_EXECUTION_ID" \
    --region $REGION

echo "Query with QueryExecutionId: $QUERY_EXECUTION_ID has been stopped."
