import base64
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Generator

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBServiceResource
    from mypy_boto3_dynamodb.service_resource import Table

from tests.db import DDB

from app.config import settings
from app.db import get_db_table
from app.main import app


def get_db_table_override() -> Generator["Table", None, None]:
    resource = next(get_ddb_resource())
    yield resource.Table(settings.ddb_table_name)


@pytest.fixture(scope="session")
def _with_app_overrides():
    app.dependency_overrides[get_db_table] = get_db_table_override


@pytest.fixture(scope="session")
def client(_with_app_overrides) -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def client_with_basic_auth(_with_app_overrides) -> TestClient:
    client = TestClient(app)
    auth_string = base64.b64encode(f"{settings.basic_auth_username}:{settings.basic_auth_password}".encode()).decode()
    client.headers.update({"Authorization": f"Basic {auth_string}"})
    return client


def get_ddb_resource():
    with mock_aws():
        yield boto3.resource("dynamodb", region_name=settings.aws_region_name)


@pytest.fixture
def ddb_resource() -> Generator["DynamoDBServiceResource", None, None]:
    yield from get_ddb_resource()


@pytest.fixture()
def ddb(ddb_resource):
    ddb = DDB(ddb_resource)
    yield ddb
    ddb.delete_table()


@pytest.fixture
def _settings():
    from app.config import settings

    return settings


@contextmanager
def mock_dependency(dependency: Callable, override: Any):
    original_override = app.dependency_overrides[dependency]
    app.dependency_overrides[dependency] = lambda: override
    try:
        yield
    finally:
        app.dependency_overrides[dependency] = original_override
