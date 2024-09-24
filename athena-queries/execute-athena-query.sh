#!/bin/bash

# Ensure a query file is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path-to-sql-file>"
    exit 1
fi

QUERY_FILE=$1

# Check if the file exists
if [ ! -f "$QUERY_FILE" ]; then
    echo "File not found: $QUERY_FILE"
    exit 1
fi

# Define the region
REGION="us-east-2"

# Load the SQL query from the file
SQL_QUERY=$(cat "$QUERY_FILE")

# WARNING: QUERIES FOR CLOUDTRAIL LOGS CAN BE VERY LARGE. ESTIMATED SIZE IS ABOUT 1.7 GIGABYTES PER DAY.
echo "WARNING: QUERIES FOR CLOUDTRAIL LOGS CAN BE VERY LARGE. ESTIMATED SIZE IS ABOUT 1.7 GIGABYTES PER DAY."

# Execute the query to create the table
aws athena start-query-execution \
    --query-string "$SQL_QUERY" \
    --query-execution-context Database=default \
    --result-configuration OutputLocation=s3://athenaqueryresults-logarchive/ \
    --region $REGION
