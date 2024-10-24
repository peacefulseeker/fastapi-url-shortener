from typing import TYPE_CHECKING, Generator

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBServiceResource

from tests.db import TestDDB

from app.config import settings
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def ddb_resource() -> Generator["DynamoDBServiceResource", None, None]:
    with mock_aws():
        conn = boto3.resource("dynamodb", region_name=settings.aws_region_name)
        yield conn


@pytest.fixture(autouse=True)
def get_ddb_resource(mocker, ddb_resource):
    return mocker.patch("app.db.get_ddb_resource", return_value=ddb_resource)


@pytest.fixture()
def ddb(ddb_resource):
    ddb = TestDDB(ddb_resource)
    ddb.create()
    yield ddb
    ddb.delete()
