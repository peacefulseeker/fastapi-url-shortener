import pytest
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST


class TestMixin:
    create_url = "/api/v1/shorten"
    payload = {
        "short_path": "test",
        "full_url": "https://example.com",
    }

    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client = client

    def _shorten_url(self, payload=payload):
        result = self.client.post(
            self.create_url,
            data=payload,
        )
        return result


@pytest.mark.usefixtures("ddb")
class TestListUrls(TestMixin):
    url = "/api/v1/list"

    def test_no_urls_created(self, client):
        result = client.get("/api/v1/list")

        assert result.status_code == HTTP_200_OK
        assert result.json() == {"count": 0, "items": []}

    def test_list_created_urls(self, client):
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

        result = client.get(self.url)
        assert result.status_code == HTTP_200_OK
        assert result.json()["count"] == 2


@pytest.mark.usefixtures("ddb")
class TestShortenUrl(TestMixin):
    def test_success(self):
        result = self._shorten_url()

        assert result.status_code == HTTP_201_CREATED
        assert result.json() == {
            "long_url": self.payload["full_url"],
            "short_path": self.payload["short_path"],
        }

    def test_duplicate_paths_disallowed(self):
        result = self._shorten_url()

        assert result.status_code == HTTP_400_BAD_REQUEST
        assert result.json() == {"detail": f"'{self.payload['short_path']}' path already exists, please use another one"}
