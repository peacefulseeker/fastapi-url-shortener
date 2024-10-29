import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tests.db import TestDDB


class TestHomePage:
    def test_success_default_url(self, client):
        response = client.get("/")

        assert "URL Shortener" in response.text
        assert str(response.context["origin"]) == "http://testserver/"
        assert response.context["frontend_assets_url"] == "/static/frontend"

    def test_versioned_assets_cloudfront_url(self, client):
        from app.config import settings

        settings.frontend_assets_version = "202410291028_73bc2b9"
        settings.aws_cloudfront_domain = "cdn.example.com"

        response = client.get("/")
        assert response.context["frontend_assets_url"] == "https://cdn.example.com/fus/v/202410291028_73bc2b9"


@pytest.mark.usefixtures("ddb")
class TestCatchAllRedirect:
    def _put_item(self, ddb: TestDDB):
        ddb.table.put_item(  # type: ignore
            Item={
                "ShortPath": "test",
                "FullUrl": "https://example.com",
            },
        )

    def test_redirects_to_homepage_when_path_not_found(self, client: TestClient):
        response = client.get("/not_yet_there")

        assert response.status_code == status.HTTP_304_NOT_MODIFIED
        assert response.headers["location"] == "http://testserver/"

    def test_redirects_to_full_url_when_path_found(self, client: TestClient, ddb: TestDDB):
        self._put_item(ddb)

        response = client.get("/test")

        assert response.url == "https://example.com"
        assert response.history[0].status_code == status.HTTP_302_FOUND
        assert response.status_code == status.HTTP_200_OK

    def test_visits_attribute_increments_by_one(self, client: TestClient, ddb: TestDDB):
        self._put_item(ddb)

        visits = 5
        for _ in range(visits):
            client.get("/test")

        response = ddb.table.get_item(Key={"ShortPath": "test"})  # type: ignore
        assert response.get("Item", {})["Visits"] == visits
