from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.urls.url_shortener import ExistingUrlItem, ShortenUrlForm, UrlShortener
from app.config import settings
from app.db import get_db_table
from app.dependencies import require_basic_auth

router = APIRouter(prefix="/urls")
limiter = Limiter(key_func=get_remote_address)


@router.get("", dependencies=[Depends(require_basic_auth)])
async def list_urls() -> dict:
    table = get_db_table()
    response = table.scan()
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


@router.post("/shorten")
@limiter.limit(
    "5/minute",
    error_message="Hold on, too many requests.",
    exempt_when=lambda: settings.debug,
)
async def shorten_url(request: Request, data: Annotated[ShortenUrlForm, Form()], response: Response) -> dict:
    item = UrlShortener(data).item

    if isinstance(item, ExistingUrlItem):
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_201_CREATED

    return {
        "detail": {
            "short_path": item.short_path,
            "shortened_url": str(request.base_url.replace(path=item.short_path)),
            "expires_at": item.expires_at,
        },
    }
