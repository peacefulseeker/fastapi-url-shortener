from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.config import settings
from app.views import catch_all_redirect, home

app = FastAPI(docs_url="/api/v1/docs", redoc_url=None)

if settings.debug:
    app.mount("/static", StaticFiles(directory="app/static", check_dir=False), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=settings.cors_allowed_methods,
)

app.add_api_route("/", home)
app.include_router(v1_router)
app.add_api_route("/{path:path}", catch_all_redirect, methods=["GET"])
