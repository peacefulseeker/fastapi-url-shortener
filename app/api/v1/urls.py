import random
import string
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Annotated, Optional

import botocore
import botocore.exceptions
from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from pydantic import AliasGenerator, BaseModel, ConfigDict, alias_generators
from slowapi import Limiter
from slowapi.util import get_remote_address

if TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_dynamodb.type_defs import ScanOutputTableTypeDef

from app.config import settings
from app.db import get_db_table
from app.dependencies import require_basic_auth

router = APIRouter(prefix="/urls")
limiter = Limiter(key_func=get_remote_address)


class ShortenUrlForm(BaseModel):
    short_path: str = Form()
    full_url: str = Form()


class UrlItem(BaseModel):
    short_path: Optional[str]
    full_url: str
    created_at: str
    expires_at: int = int((datetime.now() + timedelta(days=settings.url_expiration_in_days)).timestamp())

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=alias_generators.to_pascal),
    )


class ExistingUrlItem(BaseModel):
    short_path: str
    expires_at: int

    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=alias_generators.to_pascal),
    )


def _generate_random_short_path(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def _find_existing_url(table: "Table", full_url: str) -> dict | None:
    response = table.query(
        IndexName="FullUrl-index",
        KeyConditionExpression=Key("FullUrl").eq(full_url),
    )
    return response["Items"][0] if response.get("Items") else None


def _put_random_url_item(table: "Table", data: ShortenUrlForm) -> UrlItem | ExistingUrlItem:
    existing_item = _find_existing_url(table, data.full_url)
    if existing_item:
        return ExistingUrlItem(**existing_item)

    while True:
        try:
            data.short_path = _generate_random_short_path()
            item = _construct_url_item(data)
            table.put_item(
                Item=item.model_dump(by_alias=True),
                ConditionExpression="attribute_not_exists(ShortPath)",
            )
            return item
        except botocore.exceptions.ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                continue
            raise


def _put_custom_url_item(table: "Table", data: ShortenUrlForm) -> UrlItem:
    try:
        item = _construct_url_item(data)
        table.put_item(
            Item=item.model_dump(by_alias=True),
            ConditionExpression="attribute_not_exists(ShortPath)",
        )
    except botocore.exceptions.ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{data.short_path}' path already exists, please use another one",
            )

        raise exc
    return item


def _construct_url_item(data: ShortenUrlForm) -> UrlItem:
    return UrlItem(
        short_path=data.short_path,
        full_url=data.full_url,
        created_at=datetime.now().isoformat(),
    )


@router.get("", dependencies=[Depends(require_basic_auth)])
async def list_urls() -> dict:
    table = get_db_table()
    response: "ScanOutputTableTypeDef" = table.scan()
    count = response["Count"]

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        response["Items"].extend(response["Items"])
        count += response["Count"]

    return {
        "detail": {
            "count": count,
            "items": response["Items"],
        }
    }


@router.post("/shorten", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute", error_message="Hold on, too many requests.", exempt_when=lambda: settings.debug)
async def shorten_url(request: Request, data: Annotated[ShortenUrlForm, Form()]) -> dict:
    table = get_db_table()
    if data.short_path:
        item = _put_custom_url_item(table, data)
    else:
        item = _put_random_url_item(table, data)

    return {
        "detail": {
            "shortened_url": str(request.base_url.replace(path=item.short_path)),
            "expires_at": item.expires_at,
        },
    }
