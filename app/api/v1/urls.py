from datetime import datetime
from typing import TYPE_CHECKING, Annotated

import botocore
import botocore.exceptions
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

if TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_dynamodb.type_defs import ScanOutputTableTypeDef

from app.config import settings
from app.db import get_db_table
from app.dependencies import require_basic_auth

router = APIRouter(prefix="/urls")
limiter = Limiter(key_func=get_remote_address)


class ShortenUrlForm(BaseModel):
    short_path: str = Form()
    full_url: str = Form()


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

    try:
        table.put_item(
            Item={"ShortPath": data.short_path, "FullUrl": data.full_url, "CreatedAt": str(datetime.now())},
            ConditionExpression="attribute_not_exists(ShortPath)",
        )
    except botocore.exceptions.ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{data.short_path}' path already exists, please use another one",
            )

        raise exc

    return {
        "detail": {
            "shortened_url": str(request.base_url.replace(path=data.short_path)),
        }
    }
