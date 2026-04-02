import pytest
from pytest_mock import MockType
import httpx

from moneysnake.client import make_request
from moneysnake.exceptions import (
    MoneybirdAPIError,
    MoneybirdError,
    MoneybirdNotFoundError,
    MoneybirdRateLimitError,
    MoneybirdValidationError,
)


def test_exception_hierarchy():
    """All API errors should inherit from MoneybirdError."""
    assert issubclass(MoneybirdAPIError, MoneybirdError)
    assert issubclass(MoneybirdNotFoundError, MoneybirdAPIError)
    assert issubclass(MoneybirdValidationError, MoneybirdAPIError)
    assert issubclass(MoneybirdRateLimitError, MoneybirdAPIError)


def test_api_error_attributes():
    err = MoneybirdAPIError(
        status_code=400,
        response_body="Bad request",
        method="post",
        path="contacts",
    )
    assert err.status_code == 400
    assert err.response_body == "Bad request"
    assert err.method == "post"
    assert err.path == "contacts"
    assert "POST contacts returned 400" in str(err)


def test_404_raises_not_found(mocker: MockType):
    response = httpx.Response(
        404, text="Not found", request=httpx.Request("GET", "http://test")
    )
    mocker.patch("moneysnake.client.httpx.request", return_value=response)

    with pytest.raises(MoneybirdNotFoundError) as exc_info:
        make_request("contacts/1", method="get")

    assert exc_info.value.status_code == 404


def test_422_raises_validation_error(mocker: MockType):
    response = httpx.Response(
        422, text="Unprocessable", request=httpx.Request("POST", "http://test")
    )
    mocker.patch("moneysnake.client.httpx.request", return_value=response)

    with pytest.raises(MoneybirdValidationError) as exc_info:
        make_request("contacts", method="post")

    assert exc_info.value.status_code == 422


def test_429_raises_rate_limit_error(mocker: MockType):
    response = httpx.Response(
        429, text="Too many requests", request=httpx.Request("GET", "http://test")
    )
    mocker.patch("moneysnake.client.httpx.request", return_value=response)

    with pytest.raises(MoneybirdRateLimitError) as exc_info:
        make_request("contacts", method="get")

    assert exc_info.value.status_code == 429


def test_500_raises_generic_api_error(mocker: MockType):
    response = httpx.Response(
        500, text="Internal error", request=httpx.Request("GET", "http://test")
    )
    mocker.patch("moneysnake.client.httpx.request", return_value=response)

    with pytest.raises(MoneybirdAPIError) as exc_info:
        make_request("contacts", method="get")

    assert exc_info.value.status_code == 500
    assert type(exc_info.value) is MoneybirdAPIError
