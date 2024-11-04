from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import urls_api
from app.config import settings
from app.sentry import init_sentry
from app.views import catch_all_redirect, home

init_sentry()
app = FastAPI(docs_url="/api/v1/docs", redoc_url=None)

app.mount("/static", StaticFiles(directory="app/static", check_dir=False), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=settings.cors_allowed_methods,
)
app.add_api_route("/", home, name="home")
app.include_router(urls_api.router, prefix="/api/v1")
app.add_api_route("/{path:path}", catch_all_redirect, methods=["GET"])
