import pytest
from fastapi.testclient import TestClient

from tests.db import TestDDB

from app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def ddb():
    ddb = TestDDB()
    ddb.create()
    yield ddb
    ddb.delete()
