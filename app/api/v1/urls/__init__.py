from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.urls.url_shortener import ExistingUrlItem, ShortenUrlForm, UrlShortener
from app.config import settings
from app.dependencies import GetDBTable, require_basic_auth


class UrlsAPI:
    def __init__(self) -> None:
        self.limiter = Limiter(key_func=get_remote_address)

    @property
    def router(self) -> APIRouter:
        api_router = APIRouter(prefix="/urls", tags=["urls"])

        @api_router.get("/{short_path}", dependencies=[Depends(require_basic_auth)])
        def get(short_path: str, table: GetDBTable) -> dict:
            return table.get_item(Key={"ShortPath": short_path}).get("Item", {})

        @api_router.get("", dependencies=[Depends(require_basic_auth)])
        def list_all(table: GetDBTable) -> dict:
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

        @api_router.post("/shorten")
        @self.limiter.limit(
            "5/minute",
            error_message="Hold on, too many requests.",
            exempt_when=lambda: settings.debug or settings.loadtest,
        )
        def shorten_url(request: Request, data: Annotated[ShortenUrlForm, Form()], response: Response, table: GetDBTable) -> dict:
            item = UrlShortener(data, table).item

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

        return api_router
