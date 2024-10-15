ARG PYTHON_VERSION=3.11-slim-bullseye

from python:${PYTHON_VERSION} as poetry-deps-export
    WORKDIR /

    RUN pip install poetry
    COPY pyproject.toml poetry.lock /
    RUN poetry config virtualenvs.create false
    RUN poetry install --no-root --no-interaction
    RUN poetry export --without-hashes --format=requirements.txt --output requirements.txt

FROM python:${PYTHON_VERSION} as backend-build

    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    RUN useradd --user-group --system --no-log-init --create-home appuser

    RUN apt-get update && apt-get install -y \
        libpq-dev \
        gcc \
        && rm -rf /var/lib/apt/lists/*

    COPY --from=poetry-deps-export /requirements.txt /
    RUN pip install --no-cache-dir -r requirements.txt

FROM backend-build as app
    WORKDIR /app

    # TODO: copy only the files that are needed for launching app in prod
    COPY . /app/

    RUN chown -R appuser .
    USER appuser


FROM app as web
    EXPOSE 8080

    CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8080"]




