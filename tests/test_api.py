from unittest.mock import patch

import botocore.exceptions
import pytest
from fastapi.testclient import TestClient
from starlette import status

pytestmark = pytest.mark.usefixtures("ddb")


class TestMixin:
    shorten_url = "/api/v1/shorten"
    payload = {
        "short_path": "test",
        "full_url": "https://example.com",
    }

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client: TestClient = client

    def _shorten_url(self, payload=payload):
        result = self.client.post(
            self.shorten_url,
            data=payload,
        )
        return result

    def _simulate_prod(self):
        from app.config import settings

        settings.debug = False


class TestListUrls(TestMixin):
    url = "/api/v1/list"

    def test_basic_auth_required(self):
        result = self.client.get(self.url)

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {"detail": "Not authenticated"}
        assert result.headers["WWW-Authenticate"] == "Basic"

    def test_no_urls_created(self, client_with_basic_auth):
        result = client_with_basic_auth.get("/api/v1/list")

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["detail"] == {"count": 0, "items": []}

    def test_list_created_urls(self, client_with_basic_auth):
        self._shorten_url(
            payload={
                "short_path": "ya",
                "full_url": "https://ya.ru",
            },
        )
        self._shorten_url(
            payload={
                "short_path": "go",
                "full_url": "https://google.com",
            },
        )

        result = client_with_basic_auth.get(self.url)
        assert result.status_code == status.HTTP_200_OK
        assert result.json()["detail"]["count"] == 2


@pytest.mark.usefixtures("ddb")
class TestShortenUrl(TestMixin):
    def test_success(self):
        self.payload["short_path"] = "google"

        result = self._shorten_url()

        assert result.status_code == status.HTTP_201_CREATED
        assert result.json()["detail"] == {"shortened_url": "http://testserver/google"}  # pytest defined

    def test_duplicate_paths_disallowed(self):
        self._shorten_url()

        result = self._shorten_url()

        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert result.json() == {"detail": f"'{self.payload['short_path']}' path already exists, please use another one"}

    def test_exceptions_reraised(self):
        side_effect = botocore.exceptions.ClientError(
            error_response={"Error": {"Message": "Failed retrieving Table"}},
            operation_name="boto3.resource.Table",
        )
        with patch("app.api.v1.get_db_table", side_effect=side_effect):
            with pytest.raises(botocore.exceptions.ClientError) as exc:
                self._shorten_url()

        assert exc.value.response.get("Error", {}).get("Message") == "Failed retrieving Table"

    def test_throttled(self):
        self._simulate_prod()

        for _ in range(5):
            self._shorten_url()

        result = self._shorten_url()

        assert result.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert result.json() == {"detail": "Hold on, too many requests."}
