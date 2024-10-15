import boto3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

from app import config


def get_db_table(table='Urls') -> "Table":
    resource: "DynamoDBServiceResource" = boto3.resource(
        'dynamodb',
        endpoint_url=config.DDB_ENDPOINT_URL,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION_NAME,
    )
    return resource.Table(table)

