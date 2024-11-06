import random
import string
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

import botocore
import botocore.exceptions
from boto3.dynamodb.conditions import Key
from fastapi import Form, HTTPException, status
from pydantic import AliasGenerator, BaseModel, ConfigDict, alias_generators

if TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_dynamodb.service_resource import Table

from app.config import settings


class ShortenUrlForm(BaseModel):
    short_path: str = Form()
    full_url: str = Form()

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class UrlItem(BaseModel):
    short_path: Optional[str]
    full_url: str
    created_at: str
    expires_at: int = int((datetime.now() + timedelta(seconds=settings.url_ttl)).timestamp())

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=alias_generators.to_pascal),
    )


class ExistingUrlItem(BaseModel):
    short_path: str
    expires_at: int

    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=alias_generators.to_pascal),
    )


class UrlShortener:
    def __init__(self, data: ShortenUrlForm, table: "Table") -> None:
        self.table = table
        self.data = data.model_copy()
        self.item: UrlItem | ExistingUrlItem = self._create_item()

    @staticmethod
    def generate_random_short_path(length: int = 8) -> str:
        chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))

    def _find_existing_url(self) -> dict | None:
        response = self.table.query(
            IndexName="FullUrl-index",
            KeyConditionExpression=Key("FullUrl").eq(self.data.full_url),
        )
        return response["Items"][0] if response.get("Items") else None

    def _create_item(self) -> UrlItem | ExistingUrlItem:
        if self.data.short_path:
            return self._put_custom_url_item()
        return self._put_random_url_item()

    def _put_random_url_item(self) -> UrlItem | ExistingUrlItem:
        existing_item = self._find_existing_url()
        if existing_item:
            return ExistingUrlItem(**existing_item)

        while True:
            try:
                self.data.short_path = self.generate_random_short_path()
                item = self._construct_url_item()
                self.table.put_item(
                    Item=item.model_dump(by_alias=True),
                    ConditionExpression="attribute_not_exists(ShortPath)",
                )
                return item
            except botocore.exceptions.ClientError as exc:
                if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                    continue
                raise exc

    def _put_custom_url_item(self) -> UrlItem:
        try:
            item = self._construct_url_item()
            self.table.put_item(
                Item=item.model_dump(by_alias=True),
                ConditionExpression="attribute_not_exists(ShortPath)",
            )
        except botocore.exceptions.ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{self.data.short_path}' path is taken, please use another one",
                )

            raise exc
        return item

    def _construct_url_item(self) -> UrlItem:
        return UrlItem(
            short_path=self.data.short_path,
            full_url=self.data.full_url,
            created_at=datetime.now().isoformat(),
        )
