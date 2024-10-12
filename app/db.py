import boto3
from mypy_boto3_dynamodb import  DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table


def scan_table(table='Urls') -> None:
    table = get_db_table()
    response = table.scan()
    for item in response['Items']:
        print(item)


def get_db_table(table='Urls') -> Table:
    resource: DynamoDBServiceResource = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:7654',
    )
    return resource.Table(table)

