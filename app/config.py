from functools import lru_cache

from fastapi.templating import Jinja2Templates
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsMixin:
    @staticmethod
    def parse_comma_separated_values(setting: str | tuple[str, ...]) -> tuple[str, ...]:
        if isinstance(setting, str):  # pragma: no cover
            return tuple(item.strip() for item in setting.split(","))
        return setting


class DatabaseSettings(BaseSettings):
    ddb_table_name: str = Field(default="Urls")
    ddb_endpoint_url: str = Field(default="http://localhost:7654")
    aws_access_key_id: str = Field(default="local")
    aws_secret_access_key: str = Field(default="local")
    aws_region_name: str = Field(default="local")


class AuthSettings(BaseSettings):
    basic_auth_username: str = Field(default="")
    basic_auth_password: str = Field(default="")


class CorsSettings(SettingsMixin, BaseSettings):
    cors_allowed_origins: str | tuple[str, ...] = Field(default=("*",))
    cors_allowed_methods: str | tuple[str, ...] = Field(default=("POST", "GET"))

    @field_validator("cors_allowed_origins", "cors_allowed_methods", mode="before")
    def parse_comma_separated_values(cls, setting: str | tuple[str, ...]) -> tuple[str, ...]:
        return super().parse_comma_separated_values(setting)


class DevelopmentSettings(BaseSettings):
    debug: bool = Field(default=False)
    loadtest: bool = Field(default=False)
    loadtest_host: str = Field(default="")
    vite_origin: str = Field(default="http://localhost:5555")


class Settings(DatabaseSettings, CorsSettings, AuthSettings, DevelopmentSettings):
    model_config = SettingsConfigDict(env_file="app/.env", env_file_encoding="utf-8")

    aws_cloudfront_domain: str = Field(default="")
    frontend_assets_version: str = Field(default="")

    url_ttl: int = Field(default=60 * 60 * 24 * 30)  # 30 days

    sentry_dsn: str = Field(default="")

    @classmethod
    @lru_cache
    def load(cls) -> "Settings":
        return cls()


settings = Settings.load()
templates = Jinja2Templates(directory="app/templates")
