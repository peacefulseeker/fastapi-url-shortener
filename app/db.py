from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from app.config import settings


def get_db_table(table="Urls") -> "Table":
    resource: "DynamoDBServiceResource" = boto3.resource(
        "dynamodb",
        endpoint_url=settings.ddb_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region_name,
    )
    return resource.Table(table)
