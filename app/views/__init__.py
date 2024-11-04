import starlette.status as status
from fastapi import BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from app.config import settings, templates
from app.db import GetDBTable
from app.tasks import increment_url_visits


def get_frontend_assets_url() -> str:
    if settings.frontend_assets_version:
        return f"https://{settings.aws_cloudfront_domain}/fus/v/{settings.frontend_assets_version}"
    return "/static/frontend"


def home(request: Request) -> _TemplateResponse:
    context: dict = {
        "origin": request.base_url,
    }
    if settings.debug:
        context["vite_origin"] = settings.vite_origin
    else:
        context["frontend_assets_url"] = get_frontend_assets_url()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


def catch_all_redirect(path: str, request: Request, table: GetDBTable, background_tasks: BackgroundTasks) -> RedirectResponse:
    response = table.get_item(Key={"ShortPath": path})

    if "Item" not in response:
        return RedirectResponse(request.url_for("home"), status_code=status.HTTP_304_NOT_MODIFIED)

    full_url = str(response["Item"]["FullUrl"])
    background_tasks.add_task(increment_url_visits, path, table)

    return RedirectResponse(full_url, status_code=status.HTTP_302_FOUND)
