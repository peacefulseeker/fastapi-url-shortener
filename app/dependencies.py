import secrets
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

if TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_dynamodb.service_resource import Table

from app.config import settings
from app.db import get_db_table

http_basic_auth = HTTPBasic()


def require_basic_auth(credentials: Annotated[HTTPBasicCredentials, Depends(http_basic_auth)]):
    username, password = credentials.username.encode(), credentials.password.encode()
    username_valid = secrets.compare_digest(username, settings.basic_auth_username.encode())
    password_valid = secrets.compare_digest(password, settings.basic_auth_password.encode())

    if not (username_valid and password_valid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


GetDBTable = Annotated["Table", Depends(get_db_table)]
