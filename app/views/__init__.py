from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
import starlette.status as status

from app.db import get_db_table

templates = Jinja2Templates(directory="templates")


async def home(request: Request) -> _TemplateResponse:
     return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


async def catch_all(path: str, request: Request) -> RedirectResponse:
    table = get_db_table()
    response = table.get_item(Key={"ShortPath": path})

    if "Item" not in response:
        return RedirectResponse(request.url_for('home'), status_code=status.HTTP_304_NOT_MODIFIED)

    full_url = str(response["Item"]["FullUrl"])
    return RedirectResponse(full_url, status_code=status.HTTP_302_FOUND)
