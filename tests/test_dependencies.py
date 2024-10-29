import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from app.dependencies import require_basic_auth


class TestRequireBasicAuth:
    def test_valid_basic_auth(self):
        credentials = HTTPBasicCredentials(username="hello", password="world")
        result = require_basic_auth(credentials)
        assert result is None

    def test_invalid_basic_auth(self):
        credentials = HTTPBasicCredentials(username="oops", password="I, did it again")

        with pytest.raises(HTTPException) as exc:
            require_basic_auth(credentials)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid credentials"
        assert exc.value.headers == {"WWW-Authenticate": "Basic"}
