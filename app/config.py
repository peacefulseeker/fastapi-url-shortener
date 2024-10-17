from functools import lru_cache

from fastapi.templating import Jinja2Templates
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsMixin:
    @staticmethod
    def parse_comma_separated_values(setting: str | tuple[str, ...]) -> tuple[str, ...]:
        if isinstance(setting, str):
            return tuple(item.strip() for item in setting.split(","))
        return setting


class DatabaseSettings(BaseSettings):
    ddb_table_name: str = Field(default="Urls")
    ddb_endpoint_url: str = Field(default="http://localhost:7654")
    aws_access_key_id: str = Field(default="local")
    aws_secret_access_key: str = Field(default="local")
    aws_region_name: str = Field(default="local")


class CorsSettings(SettingsMixin, BaseSettings):
    cors_allowed_origins: str | tuple[str, ...] = Field(default=("*",))
    cors_allowed_methods: str | tuple[str, ...] = Field(default=("POST", "GET"))

    @field_validator("cors_allowed_origins", "cors_allowed_methods", mode="before")
    def parse_comma_separated_values(cls, setting: str | tuple[str, ...]) -> tuple[str, ...]:
        return super().parse_comma_separated_values(setting)


class Settings(DatabaseSettings, CorsSettings):
    model_config = SettingsConfigDict(env_file="app/.env", env_file_encoding="utf-8")

    @classmethod
    @lru_cache
    def load(cls) -> "Settings":
        return cls()


settings = Settings.load()
templates = Jinja2Templates(directory="app/templates")
