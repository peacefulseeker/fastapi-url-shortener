class TestHomePage:
    def test_success_default_url(self, client):
        response = client.get("/")

        assert "Shorten URLs effortlessly" in response.text
        assert str(response.context["origin"]) == "http://testserver/"
        assert response.context["frontend_assets_url"] == "/static/frontend"

    def test_versioned_assets_cloudfront_url(self, client, _settings):
        _settings.frontend_assets_version = "202410291028_73bc2b9"
        _settings.aws_cloudfront_domain = "cdn.example.com"

        response = client.get("/")
        assert response.context["frontend_assets_url"] == "https://cdn.example.com/fus/v/202410291028_73bc2b9"
        assert "vite_origin" not in response.context

    def test_debug_mode_expects_vite_origin(self, client, _settings):
        _settings.debug = True

        response = client.get("/")

        assert "frontend_assets_url" not in response.context
        assert response.context["vite_origin"] == _settings.vite_origin
