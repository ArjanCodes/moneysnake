from unittest.mock import patch

import httpx
import pytest
from pytest_mock import MockType

import moneysnake.client as client
from moneysnake.client import make_request, set_max_retries
from moneysnake.exceptions import (
    MoneybirdAPIError,
    MoneybirdNotFoundError,
    MoneybirdRateLimitError,
)


@pytest.fixture(autouse=True)
def _reset_retries():
    """Reset max_retries to default after each test."""
    original = client.max_retries_
    yield
    client.max_retries_ = original


def _make_response(status_code: int, json_data: dict | None = None, headers: dict | None = None) -> httpx.Response:
    content = b""
    if json_data is not None:
        import json
        content = json.dumps(json_data).encode()
    resp = httpx.Response(
        status_code,
        content=content,
        headers=headers or {},
        request=httpx.Request("GET", "https://example.com"),
    )
    return resp


class TestRetryOn429:
    def test_retries_on_429_then_succeeds(self, mocker: MockType):
        set_max_retries(2)
        mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(429, headers={"Retry-After": "0"}),
            _make_response(200, json_data={"id": 1}),
        ]
        mock_request = mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        result = make_request("contacts/1", method="get")
        assert result == {"id": 1}
        assert mock_request.call_count == 2

    def test_retries_exhausted_raises_rate_limit(self, mocker: MockType):
        set_max_retries(1)
        mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(429, headers={"Retry-After": "0"}),
            _make_response(429),
        ]
        mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        with pytest.raises(MoneybirdRateLimitError):
            make_request("contacts/1", method="get")


class TestRetryOn5xx:
    def test_retries_on_500_then_succeeds(self, mocker: MockType):
        set_max_retries(2)
        mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(500),
            _make_response(200, json_data={"id": 1}),
        ]
        mock_request = mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        result = make_request("contacts/1", method="get")
        assert result == {"id": 1}
        assert mock_request.call_count == 2

    def test_retries_on_502(self, mocker: MockType):
        set_max_retries(1)
        mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(502),
            _make_response(200, json_data={"ok": True}),
        ]
        mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        result = make_request("test", method="get")
        assert result == {"ok": True}

    def test_retries_exhausted_raises_api_error(self, mocker: MockType):
        set_max_retries(1)
        mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(500),
            _make_response(500),
        ]
        mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        with pytest.raises(MoneybirdAPIError) as exc_info:
            make_request("contacts/1", method="get")
        assert exc_info.value.status_code == 500


class TestNoRetryOnMutating5xx:
    def test_post_500_not_retried(self, mocker: MockType):
        set_max_retries(3)
        mock_request = mocker.patch(
            "moneysnake.client.httpx.request",
            return_value=_make_response(500),
        )
        with pytest.raises(MoneybirdAPIError):
            make_request("contacts", method="post", data={"name": "test"})
        assert mock_request.call_count == 1

    def test_patch_502_not_retried(self, mocker: MockType):
        set_max_retries(3)
        mock_request = mocker.patch(
            "moneysnake.client.httpx.request",
            return_value=_make_response(502),
        )
        with pytest.raises(MoneybirdAPIError):
            make_request("contacts/1", method="patch", data={"name": "test"})
        assert mock_request.call_count == 1

    def test_post_429_still_retried(self, mocker: MockType):
        """429 rate limits should be retried regardless of HTTP method."""
        set_max_retries(1)
        mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(429, headers={"Retry-After": "1"}),
            _make_response(200, json_data={"id": 1}),
        ]
        mock_request = mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        result = make_request("contacts", method="post", data={"name": "test"})
        assert result == {"id": 1}
        assert mock_request.call_count == 2


class TestNoRetryOnClientErrors:
    def test_404_not_retried(self, mocker: MockType):
        set_max_retries(3)
        mock_request = mocker.patch(
            "moneysnake.client.httpx.request",
            return_value=_make_response(404),
        )
        with pytest.raises(MoneybirdNotFoundError):
            make_request("contacts/999", method="get")
        assert mock_request.call_count == 1

    def test_422_not_retried(self, mocker: MockType):
        set_max_retries(3)
        mock_request = mocker.patch(
            "moneysnake.client.httpx.request",
            return_value=_make_response(422),
        )
        with pytest.raises(MoneybirdAPIError):
            make_request("contacts", method="post", data={})
        assert mock_request.call_count == 1


class TestRetryBackoff:
    def test_exponential_backoff_without_retry_after(self, mocker: MockType):
        set_max_retries(3)
        mock_sleep = mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(500),
            _make_response(500),
            _make_response(500),
            _make_response(200, json_data={"id": 1}),
        ]
        mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        make_request("test", method="get")
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1, 2, 4]  # 2^0, 2^1, 2^2

    def test_retry_after_header_respected(self, mocker: MockType):
        set_max_retries(1)
        mock_sleep = mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(429, headers={"Retry-After": "5"}),
            _make_response(200, json_data={"ok": True}),
        ]
        mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        make_request("test", method="get")
        assert mock_sleep.call_args[0][0] == 5

    def test_retry_after_invalid_falls_back_to_exponential(self, mocker: MockType):
        set_max_retries(1)
        mock_sleep = mocker.patch("moneysnake.client.time.sleep")
        responses = [
            _make_response(429, headers={"Retry-After": "Wed, 21 Oct 2025 07:28:00 GMT"}),
            _make_response(200, json_data={"ok": True}),
        ]
        mocker.patch("moneysnake.client.httpx.request", side_effect=responses)
        make_request("test", method="get")
        assert mock_sleep.call_args[0][0] == 1  # 2^0 = 1


class TestZeroRetries:
    def test_no_retries_when_max_is_zero(self, mocker: MockType):
        set_max_retries(0)
        mock_request = mocker.patch(
            "moneysnake.client.httpx.request",
            return_value=_make_response(500),
        )
        with pytest.raises(MoneybirdAPIError):
            make_request("test", method="get")
        assert mock_request.call_count == 1


class TestSetMaxRetries:
    def test_set_max_retries(self):
        set_max_retries(5)
        assert client.max_retries_ == 5
