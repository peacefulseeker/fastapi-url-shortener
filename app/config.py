from fastapi.templating import Jinja2Templates
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config("app/.env")

templates = Jinja2Templates(directory="templates")

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=CommaSeparatedStrings, default='*')
CORS_ALLOWED_METHODS = config("CORS_ALLOWED_METHODS", cast=CommaSeparatedStrings, default='POST, GET')

DDB_ENDPOINT_URL = config("DDB_ENDPOINT_URL", cast=str, default='http://localhost:7654')
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", cast=str, default='local')
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", cast=str, default='local')
AWS_REGION_NAME = config("AWS_REGION_NAME", cast=str, default='local')
