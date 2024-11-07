from unittest.mock import Mock

import pytest
import stripe
from fastapi import status

from tests.conftest import mock_dependency
from tests.db import DDB

from app.db import get_db_table


class TestCheckoutView:
    path = "/donation/checkout"

    def test_client_reference_id_required(self, client):
        response = client.get(self.path)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_response = response.json()["detail"][0]
        assert error_response["msg"] == "Field required"
        assert error_response["loc"] == ["query", "client_reference_id"]

    def test_redirects_to_stripe_checkout_url_with_short_path_as_client_reference(self, client):
        response = client.get(self.path, params={"client_reference_id": "test_unique_short_path"})

        assert response.status_code == status.HTTP_200_OK
        assert response.url == "https://donate.stripe.com?client_reference_id=test_unique_short_path"
        assert response.history[0].is_redirect


class TestSuccessView:
    path = "/donation/success"

    @pytest.fixture
    def mocked_stripe_session(self, mocker):
        return mocker.patch("app.views.donation.stripe.checkout.Session.retrieve")

    @pytest.fixture
    def mocked_sentry_sdk(self, mocker):
        return mocker.patch("app.views.donation.sentry_sdk")

    @pytest.fixture
    def mocked_table_get_item(self, mocker):
        return mocker.patch("app.views.donation.sentry_sdk")

    def test_checkout_session_id_required(self, client):
        response = client.get(self.path)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_response = response.json()["detail"][0]
        assert error_response["msg"] == "Field required"
        assert error_response["loc"] == ["query", "checkout_session_id"]

    def test_redirect_to_homepage_if_stripe_session_was_not_found(self, client, mocked_stripe_session):
        mocked_stripe_session.side_effect = stripe.InvalidRequestError(
            "No such checkout session: test_checkout_session_id",
            None,
            http_status=404,
        )

        response = client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})

        assert response.history[0].is_redirect
        assert response.url == "http://testserver/"

    def test_sentry_captures_stripe_exception(self, client, mocked_stripe_session, mocked_sentry_sdk):
        exception = stripe.InvalidRequestError(
            "Something went wrong while retrieving the session: test_checkout_session_id",
            None,
            http_status=400,
        )
        mocked_stripe_session.side_effect = exception

        client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})

        assert mocked_sentry_sdk.capture_exception.called_once_with(exception)

    def test_redirects_to_homepage_if_short_path_is_not_found(self, client, mocked_stripe_session):
        mocked_stripe_session.return_value.client_reference_id = None
        response = client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})

        assert response.history[0].is_redirect
        assert response.url == "http://testserver/"

    @pytest.mark.usefixtures("ddb")
    def test_redirects_to_homepage_if_item_not_found(self, client, mocked_stripe_session):
        mocked_stripe_session.return_value.client_reference_id = "not_found_short_path"

        response = client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})

        assert response.history[0].is_redirect
        assert response.url == "http://testserver/"

    def test_renders_success_template_for_paid_item(self, client, mocked_stripe_session):
        mocked_stripe_session.return_value.client_reference_id = "short_path"

        mocked_get_item_response = {"Item": {"StripePaymentId": "payment_id"}}
        with mock_dependency(get_db_table, Mock(get_item=Mock(return_value=mocked_get_item_response))):
            response = client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "donation_success.html"
        assert response.context["shortened_url"] == "http://testserver/short_path"
        assert response.context["payment_id"] == "payment_id"

    def test_update_item_in_table_and_renders_success_template(self, client, mocked_stripe_session, ddb: DDB):
        mocked_stripe_session.return_value = Mock(
            client_reference_id="go",
            payment_intent="payment_id",
            id="session_id",
            customer_email="customer@email.com",
        )
        ddb.put_item({"ShortPath": "go"})

        response = client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})
        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "donation_success.html"
        assert response.context["shortened_url"] == "http://testserver/go"
        assert response.context["payment_id"] == "payment_id"

        updated_item = ddb.get_item({"ShortPath": "go"})
        assert updated_item["StripePaymentId"] == "payment_id"
        assert updated_item["StripeSessionId"] == "session_id"
        assert updated_item["CustomerEmail"] == "customer@email.com"

    def test_takes_email_from_customer_details_if_present(self, client, mocked_stripe_session, ddb: DDB):
        mocked_stripe_session.return_value = Mock(
            client_reference_id="go",
            payment_intent="payment_id",
            id="session_id",
            customer_email=None,
            customer_details=Mock(email="customerdetails@email.com"),
        )
        ddb.put_item({"ShortPath": "go"})

        client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})

        updated_item = ddb.get_item({"ShortPath": "go"})
        assert updated_item["CustomerEmail"] == "customerdetails@email.com"

    def test_captures_failed_update_in_sentry_but_renders_success(self, client, mocked_stripe_session, ddb: DDB, mocked_sentry_sdk):
        mocked_stripe_session.return_value = Mock(
            client_reference_id="go",
            payment_intent="payment_id",
            id="session_id",
            customer_email="customer@email.com",
        )
        ddb.put_item({"ShortPath": "go"})

        mocked_update_item_response = {
            "ResponseMetadata": {"HTTPStatusCode": 400},
            "Attributes": {"ShortPath": "go"},
        }
        with mock_dependency(get_db_table, Mock(update_item=Mock(return_value=mocked_update_item_response))):
            response = client.get(self.path, params={"checkout_session_id": "test_checkout_session_id"})

        assert response.status_code == status.HTTP_200_OK
        assert mocked_sentry_sdk.capture_message.called_once_with(
            "Failed to update item in table",
            level="critical",
        )
        assert mocked_sentry_sdk.set_context.called_once_with("response", mocked_update_item_response)
