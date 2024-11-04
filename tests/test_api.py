from datetime import datetime
from unittest.mock import Mock

import botocore.exceptions
import pytest
from fastapi.testclient import TestClient
from starlette import status

from tests.conftest import mock_dependency

from app.api.v1 import urls
from app.api.v1.urls.url_shortener import UrlShortener
from app.db import get_db_table

pytestmark = pytest.mark.usefixtures("ddb")


class TestMixin:
    shorten_url = "/api/v1/urls/shorten"
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


class TestListUrls(TestMixin):
    url = "/api/v1/urls"

    def test_basic_auth_required(self):
        result = self.client.get(self.url)

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {"detail": "Not authenticated"}
        assert result.headers["WWW-Authenticate"] == "Basic"

    def test_no_urls_created(self, client_with_basic_auth):
        result = client_with_basic_auth.get(self.url)

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
    @pytest.fixture(autouse=True)
    def _reset_limiter(self):
        urls.limiter.reset()

    def test_success(self):
        payload = {
            "short_path": "google",
            "full_url": "https://google.com",
        }

        result = self._shorten_url(payload)

        assert result.status_code == status.HTTP_201_CREATED
        result = result.json()["detail"]

        assert result["shortened_url"] == "http://testserver/google"
        assert isinstance(result["expires_at"], int)
        assert result["expires_at"] > datetime.now().timestamp()

    def test_duplicate_paths_disallowed(self):
        self._shorten_url()

        result = self._shorten_url()

        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert result.json() == {"detail": f"'{self.payload['short_path']}' path already exists, please use another one"}

    def test_generate_random_path(self):
        result = UrlShortener.generate_random_short_path()
        assert len(result) == 8
        assert result.isalnum()

        result = UrlShortener.generate_random_short_path(12)
        assert len(result) == 12

    def test_shorten_with_custom_short_path(self):
        payload = {
            "short_path": "",
            "full_url": "https://google.com",
        }

        result = self._shorten_url(payload)
        assert result.status_code == status.HTTP_201_CREATED
        assert result.json()["detail"]["short_path"] != self.payload["short_path"]

    def test_shorten_same_full_url_returns_existing_item(self):
        payload = {
            "short_path": "",
            "full_url": "https://google.com/",
        }

        result_shortened = self._shorten_url(payload)
        result_existing = self._shorten_url(payload)

        assert result_shortened.status_code == status.HTTP_201_CREATED
        assert result_existing.status_code == status.HTTP_200_OK
        assert result_existing.json()["detail"]["short_path"] == result_shortened.json()["detail"]["short_path"]

    def test_returns_existing_item(self, mocker):
        payload_existing = {
            "short_path": "existing",
            "full_url": "https://google.com/",
        }
        self._shorten_url(payload_existing)

        payload_random = {
            "short_path": "",
            "full_url": "https://google.com/",
        }
        result = self._shorten_url(payload_random)
        assert result.status_code == status.HTTP_200_OK
        assert result.json()["detail"]["short_path"] == payload_existing["short_path"]

    def test_creates_random_path_in_loop_until_succeeds(self, mocker):
        existing_short_path = "existing"
        payload_existing = {
            "short_path": existing_short_path,
            "full_url": "https://google.com/",
        }
        mock_generate = mocker.patch(
            "app.api.v1.urls.url_shortener.UrlShortener.generate_random_short_path",
            side_effect=[
                existing_short_path,
                existing_short_path,
                "new",
            ],
        )

        self._shorten_url(payload_existing)

        payload_random = {
            "short_path": "",
            "full_url": "https://another.com/",
        }
        result = self._shorten_url(payload_random)

        assert mock_generate.call_count == 3
        assert result.status_code == status.HTTP_201_CREATED
        assert result.json()["detail"]["short_path"] == "new"

    def test_exceptions_reraised(self):
        side_effect = botocore.exceptions.ClientError(
            error_response={"Error": {"Message": "Failed inserting the item"}},
            operation_name="Table.put_item",
        )
        mocked_get_db_table = Mock()
        mocked_get_db_table.put_item.side_effect = side_effect

        with mock_dependency(get_db_table, mocked_get_db_table):
            with pytest.raises(botocore.exceptions.ClientError) as exc:
                self._shorten_url()

        assert exc.value.response.get("Error", {}).get("Message") == "Failed inserting the item"

    def test_throttled(self):
        for _ in range(5):
            self._shorten_url()

        result = self._shorten_url()

        assert result.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert result.json() == {"detail": "Hold on, too many requests."}
