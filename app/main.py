from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.views import home, catch_all_redirect
from app import config

app = FastAPI(docs_url='/api/v1/docs', redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOWED_ORIGINS,
    allow_methods=config.CORS_ALLOWED_METHODS,
    # allow_credentials=True,
    # allow_headers="*",
)

app.add_api_route('/', home)
app.include_router(v1_router)
app.add_api_route('/{path:path}', catch_all_redirect, methods=["GET"])
