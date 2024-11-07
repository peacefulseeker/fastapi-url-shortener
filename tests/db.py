from typing import TYPE_CHECKING

from app.config import settings

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table


class DDB:
    def __init__(self, ddb_resource: "DynamoDBServiceResource"):
        self.resource = ddb_resource
        self.table_name = settings.ddb_table_name
        self.table: "Table" = self.create_table()

    def create_table(self) -> "Table":
        self.resource.create_table(
            TableName=self.table_name,
            KeySchema=[{"AttributeName": "ShortPath", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "ShortPath", "AttributeType": "S"},
                {"AttributeName": "FullUrl", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "FullUrl-index",
                    "KeySchema": [{"AttributeName": "FullUrl", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "INCLUDE", "NonKeyAttributes": ["ExpiresAt"]},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
        )
        return self.resource.Table(self.table_name)

    def delete_table(self):
        self.table.delete()

    def put_item(self, item: dict) -> None:
        self.table.put_item(Item=item)

    def get_item(self, key: dict) -> dict:
        item = self.table.get_item(Key=key)
        return item["Item"] if "Item" in item else {}
