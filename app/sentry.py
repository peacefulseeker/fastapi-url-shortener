import sentry_sdk

from app.config import settings


def init_sentry():  # pragma: no cover
    if not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment="local" if settings.debug else "production",
        traces_sample_rate=0.8,
    )
