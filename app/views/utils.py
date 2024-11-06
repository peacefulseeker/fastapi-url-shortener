from fastapi import Request

from app.config import settings


def get_frontend_assets_url() -> str:
    if settings.frontend_assets_version:
        return f"https://{settings.aws_cloudfront_domain}/fus/v/{settings.frontend_assets_version}"
    return "/static/frontend"


def get_shared_template_context(request: Request) -> dict:
    context: dict = {
        "origin": request.base_url,
        "url_ttl": settings.url_ttl,
        "umami_website_id": settings.umami_website_id,
    }
    if settings.debug:
        context["vite_origin"] = settings.vite_origin
    else:
        context["frontend_assets_url"] = get_frontend_assets_url()
    return context
