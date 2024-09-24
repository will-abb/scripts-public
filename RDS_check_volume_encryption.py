import boto3


def list_rds_instances_encryption_status():
    client = boto3.client("rds")

    paginator = client.get_paginator("describe_db_instances")
    page_iterator = paginator.paginate()

    for page in page_iterator:
        for db_instance in page["DBInstances"]:
            db_identifier = db_instance["DBInstanceIdentifier"]
            encryption_status = db_instance.get("StorageEncrypted", False)
            encryption_info = "Enabled" if encryption_status else "Disabled"

            print(f"DB Instance Identifier: {db_identifier}")
            print(f"Encryption at Rest: {encryption_info}")
            print("-" * 72)


if __name__ == "__main__":
    list_rds_instances_encryption_status()
