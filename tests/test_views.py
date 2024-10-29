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
