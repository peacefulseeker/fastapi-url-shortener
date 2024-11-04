import base64
import random

from locust import HttpUser, between, run_single_user, task

from app.api.v1.urls.url_shortener import UrlShortener
from app.config import settings


class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)
    host = settings.loadtest_host
    api_prefix = "/api/v1/urls"
    short_paths = []

    def setup_basic_auth(self):
        auth_string = base64.b64encode(f"{settings.basic_auth_username}:{settings.basic_auth_password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_string}"}
        self.client.headers.update(headers)

    @task(3)
    def create_short_url(self):
        short_path = UrlShortener.generate_random_short_path()
        self.client.post(
            self.api_prefix + "/shorten",
            data={
                "full_url": "https://www.google.com",
                "short_path": short_path,
            },
        )
        self.short_paths.append(short_path)

    @task(5)
    def visit_created_short_urls(self):
        random.shuffle(self.short_paths)
        for short_path in self.short_paths:
            self.client.get(f"/{short_path}")

    @task(5)
    def visit_homepage(self):
        self.client.get("")

    @task
    def list_urls(self):
        self.setup_basic_auth()
        self.client.get("/api/v1/urls/")


# for debugging purposes
if __name__ == "__main__":
    run_single_user(URLShortenerUser)
