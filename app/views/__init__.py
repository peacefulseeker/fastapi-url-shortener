import starlette.status as status
from fastapi import BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from app.config import templates
from app.dependencies import GetDBTable
from app.tasks import increment_url_visits
from app.views.donation import DonationViews
from app.views.utils import get_shared_template_context


def home(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=get_shared_template_context(request),
    )


def catch_all_redirect(path: str, request: Request, table: GetDBTable, background_tasks: BackgroundTasks) -> RedirectResponse:
    response = table.get_item(Key={"ShortPath": path})

    if "Item" not in response:
        return RedirectResponse(request.url_for("home"), status_code=status.HTTP_304_NOT_MODIFIED)

    full_url = str(response["Item"]["FullUrl"])
    background_tasks.add_task(increment_url_visits, path, table)

    return RedirectResponse(full_url, status_code=status.HTTP_302_FOUND)


donation_views = DonationViews()
