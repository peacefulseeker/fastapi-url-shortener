from typing import TYPE_CHECKING

from app.config import settings

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table


class DDB:
    def __init__(self, ddb_resource: "DynamoDBServiceResource"):
        self.resource = ddb_resource
        self.table_name = settings.ddb_table_name
        self.table: None | Table = None

    def create_table(self) -> None:
        self.resource.create_table(
            TableName=self.table_name,
            KeySchema=[{"AttributeName": "ShortPath", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "ShortPath", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        self.table = self.resource.Table(self.table_name)

    def delete_table(self):
        if self.table:
            self.table.delete()
            self.table = None
