#!/bin/bash

# Usage: ./drop_athena_table.sh <table_name> [database_name] [region]

TABLE_NAME=$1
DATABASE_NAME=${2:-default}
REGION=${3:-us-east-2} # Default region is us-west-2 if not specified

if [ -z "$TABLE_NAME" ]; then
    echo "Usage: $0 <table_name> [database_name] [region]"
    exit 1
fi

# AWS Athena query to drop the table
QUERY_STRING="DROP TABLE IF EXISTS ${DATABASE_NAME}.${TABLE_NAME};"

# Output location for Athena query results
S3_OUTPUT="s3://athenaqueryresults-logarchive/"

# Run the Athena query to drop the table
aws athena start-query-execution \
    --query-string "$QUERY_STRING" \
    --result-configuration "OutputLocation=${S3_OUTPUT}" \
    --region "${REGION}"

echo "Drop table query submitted for ${DATABASE_NAME}.${TABLE_NAME} in region ${REGION}"
