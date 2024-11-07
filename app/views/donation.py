from typing import NewType

import sentry_sdk
import stripe
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.templating import _TemplateResponse as TemplateResponse

from app.config import settings, templates
from app.dependencies import GetDBTable
from app.views.utils import get_shared_template_context

ShortPath = NewType("ShortPath", str)


class DonationViews:
    def __init__(self) -> None:
        self.limiter = Limiter(key_func=get_remote_address)
        stripe.api_key = settings.stripe_secret_key

    @property
    def router(self) -> APIRouter:
        router = APIRouter(prefix="/donation", tags=["donation_views"])

        @router.get("/checkout", response_model=None)
        def stripe_checkout(client_reference_id: ShortPath) -> RedirectResponse:
            return RedirectResponse(settings.stripe_checkout_url + f"?client_reference_id={client_reference_id}")

        @router.get("/success", response_model=None)
        def donation_succeeded(request: Request, checkout_session_id: str, table: GetDBTable) -> RedirectResponse | TemplateResponse:
            try:
                session = stripe.checkout.Session.retrieve(checkout_session_id)
            except stripe.InvalidRequestError as exc:
                if exc.http_status != 404:
                    sentry_sdk.capture_exception(exc)
                return RedirectResponse(request.url_for("home"))

            short_path = session.client_reference_id
            if not short_path:
                return RedirectResponse(request.url_for("home"))

            response = table.get_item(Key={"ShortPath": short_path})
            item = response.get("Item", {})
            if not item:
                return RedirectResponse(request.url_for("home"))

            shortened_url = str(request.base_url.replace(path=short_path))
            if item.get("StripePaymentId"):
                context = get_shared_template_context(request) | {
                    "shortened_url": shortened_url,
                    "payment_id": item.get("StripePaymentId"),
                }

                return templates.TemplateResponse(
                    request=request,
                    name="donation_success.html",
                    context=context,
                )

            email = session.customer_email or (session.customer_details.email if session.customer_details else None)
            payment_intent = session.payment_intent
            response = table.update_item(
                Key={"ShortPath": short_path},
                UpdateExpression="REMOVE ExpiresAt SET StripeSessionId = :session_id, StripePaymentId = :payment_intent, CustomerEmail = :email",
                ExpressionAttributeValues={":payment_intent": payment_intent, ":email": email, ":session_id": session.id},
                ReturnValues="UPDATED_NEW",
            )

            # ideally should not happen, but just in case
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                sentry_sdk.set_context("response", dict(response))
                sentry_sdk.capture_message("Failed to update item in table", level="critical")

            context = get_shared_template_context(request) | {
                "shortened_url": shortened_url,
                "payment_id": payment_intent,
            }

            return templates.TemplateResponse(
                request=request,
                name="donation_success.html",
                context=context,
            )

        return router
