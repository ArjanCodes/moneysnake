import json

import httpx
import pytest
from pytest_mock import MockType

import moneysnake.client as client
from moneysnake.client import http_get_raw, http_post_file, make_request
from moneysnake.exceptions import (
    MoneybirdAPIError,
    MoneybirdConnectionError,
    MoneybirdError,
    MoneybirdNotFoundError,
    MoneybirdPermanentError,
    MoneybirdTransientError,
    MoneybirdValidationError,
)

VALIDATION_BODY = {
    "error": {"tax_number": ["is invalid"], "name": ["can't be blank"]},
    "details": {
        "tax_number": [{"error": "invalid", "value": "NL123"}],
        "name": [{"error": "blank"}],
    },
    "full_message": "Tax number is invalid, Name can't be blank",
}

NOT_FOUND_BODY = {"error": "record not found", "symbolic": {"id": "not_found"}}


@pytest.fixture(autouse=True)
def _reset_retries():
    original = client.max_retries_
    yield
    client.max_retries_ = original


def _response(status_code: int, body: str = "") -> httpx.Response:
    return httpx.Response(
        status_code, text=body, request=httpx.Request("GET", "https://example.com")
    )


def _raised(mocker: MockType, status_code: int, body: str = "", method: str = "get") -> MoneybirdError:
    client.max_retries_ = 0
    mocker.patch("moneysnake.client.httpx.request", return_value=_response(status_code, body))
    with pytest.raises(MoneybirdError) as exc_info:
        make_request("contacts", method=method)
    return exc_info.value


def test_validation_body_exposes_fields_codes_and_message(mocker: MockType):
    error = _raised(mocker, 422, json.dumps(VALIDATION_BODY), method="post")

    assert isinstance(error, MoneybirdValidationError)
    assert error.field_errors == {"tax_number": ["is invalid"], "name": ["can't be blank"]}
    assert error.field_error_codes == {"tax_number": ["invalid"], "name": ["blank"]}
    assert error.message == "Tax number is invalid, Name can't be blank"
    assert error.symbolic is None
    assert error.body == VALIDATION_BODY


def test_symbolic_body_exposes_message_and_codes(mocker: MockType):
    error = _raised(mocker, 404, json.dumps(NOT_FOUND_BODY))

    assert isinstance(error, MoneybirdNotFoundError)
    assert error.message == "record not found"
    assert error.field_errors == {}
    assert error.field_error_codes == {}
    assert error.symbolic == {"id": "not_found"}


@pytest.mark.parametrize("body", ["<html>Bad Gateway</html>", "", '["a list"]'])
def test_non_json_body_gives_raw_text_and_empty_mappings(body: str):
    error = MoneybirdAPIError(status_code=502, response_body=body, method="get", path="contacts")

    assert error.message == body
    assert error.field_errors == {}
    assert error.field_error_codes == {}
    assert error.symbolic is None
    assert str(error) == f"GET contacts returned 502: {body}"


@pytest.mark.parametrize("status_code", [429, 500, 503])
def test_transient_status_codes(mocker: MockType, status_code: int):
    error = _raised(mocker, status_code)

    assert isinstance(error, MoneybirdTransientError)
    assert not isinstance(error, MoneybirdPermanentError)
    assert isinstance(error, MoneybirdAPIError)


@pytest.mark.parametrize("status_code", [400, 401, 402, 403, 404, 405, 422])
def test_permanent_status_codes(mocker: MockType, status_code: int):
    error = _raised(mocker, status_code)

    assert isinstance(error, MoneybirdPermanentError)
    assert not isinstance(error, MoneybirdTransientError)
    assert isinstance(error, MoneybirdAPIError)


def test_connection_error_is_transient_and_not_an_api_error(mocker: MockType):
    client.max_retries_ = 0
    mocker.patch("moneysnake.client.httpx.request", side_effect=httpx.ConnectError("refused"))

    with pytest.raises(MoneybirdConnectionError) as exc_info:
        make_request("contacts", method="get")

    error = exc_info.value
    assert isinstance(error, MoneybirdTransientError)
    assert isinstance(error, MoneybirdError)
    assert not isinstance(error, MoneybirdAPIError)
    assert (error.method, error.path) == ("get", "contacts")


def test_connection_error_on_get_is_retried_then_raised(mocker: MockType):
    client.max_retries_ = 2
    mock_sleep = mocker.patch("moneysnake.client.time.sleep")
    mock_request = mocker.patch(
        "moneysnake.client.httpx.request", side_effect=httpx.ConnectError("refused")
    )

    with pytest.raises(MoneybirdConnectionError) as exc_info:
        make_request("contacts/1", method="get")

    assert mock_request.call_count == 3
    assert [call.args[0] for call in mock_sleep.call_args_list] == [1, 2]
    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)


def test_timeout_on_get_is_retried_then_succeeds(mocker: MockType):
    client.max_retries_ = 1
    mocker.patch("moneysnake.client.time.sleep")
    mocker.patch(
        "moneysnake.client.httpx.request",
        side_effect=[httpx.ReadTimeout("slow"), _response(200, '{"id": 1}')],
    )

    assert make_request("contacts/1", method="get") == {"id": 1}


def test_connection_error_on_post_is_not_retried(mocker: MockType):
    client.max_retries_ = 3
    mock_sleep = mocker.patch("moneysnake.client.time.sleep")
    mock_request = mocker.patch(
        "moneysnake.client.httpx.request", side_effect=httpx.ConnectError("refused")
    )

    with pytest.raises(MoneybirdConnectionError) as exc_info:
        make_request("contacts", method="post", data={"name": "test"})

    assert mock_request.call_count == 1
    mock_sleep.assert_not_called()
    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)


@pytest.mark.parametrize(
    "call",
    [
        lambda: http_get_raw("sales_invoices/1/download_pdf"),
        lambda: http_post_file("documents/1/attachments", field="file", filename="a", content=b""),
    ],
    ids=["download", "upload"],
)
def test_download_and_upload_wrap_transport_error_without_retry(mocker: MockType, call):
    client.max_retries_ = 3
    mock_request = mocker.patch(
        "moneysnake.client.httpx.request", side_effect=httpx.ConnectTimeout("timed out")
    )

    with pytest.raises(MoneybirdConnectionError) as exc_info:
        call()

    assert mock_request.call_count == 1
    assert isinstance(exc_info.value.__cause__, httpx.ConnectTimeout)
