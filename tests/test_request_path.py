from typing import Any

import httpx
import pytest
from pytest_mock import MockType

import moneysnake.client as client
from moneysnake.client import http_get, http_get_raw, http_post_file
from moneysnake.exceptions import MoneybirdAPIError, MoneybirdNotFoundError
from moneysnake.sales_invoice import SalesInvoice


def _response(status_code: int, **kwargs: Any) -> httpx.Response:
    return httpx.Response(
        status_code, request=httpx.Request("GET", "https://example.com"), **kwargs
    )


def _route_through(transport: httpx.MockTransport):
    def request(method: str, url: str, *, timeout: Any, **kwargs: Any) -> httpx.Response:
        with httpx.Client(transport=transport, timeout=timeout) as http:
            return http.request(method, url, **kwargs)

    return request


def test_json_upload_and_download_share_one_send_function(mocker: MockType):
    mock_send = mocker.patch(
        "moneysnake.client._send", return_value=_response(200, json={"id": 1})
    )

    assert http_get("contacts/1") == {"id": 1}
    assert http_post_file(
        "documents/1/attachments", field="file", filename="a.pdf", content=b"%PDF"
    ) == {"id": 1}
    assert http_get_raw("sales_invoices/1/download_pdf").status_code == 200

    assert [call.args for call in mock_send.call_args_list] == [
        ("get", "contacts/1"),
        ("post", "documents/1/attachments"),
        ("get", "sales_invoices/1/download_pdf"),
    ]


def test_download_pdf_of_missing_invoice_raises_not_found(mocker: MockType):
    mocker.patch(
        "moneysnake.client.httpx.request", return_value=_response(404, text="Not found")
    )

    with pytest.raises(MoneybirdNotFoundError) as exc_info:
        SalesInvoice(id="1").download_pdf()

    assert exc_info.value.status_code == 404
    assert exc_info.value.path == "sales_invoices/1/download_pdf"


@pytest.mark.parametrize(
    "call",
    [
        lambda: http_get_raw("sales_invoices/1/download_pdf"),
        lambda: http_post_file("documents/1/attachments", field="file", filename="a", content=b""),
    ],
    ids=["download", "upload"],
)
def test_download_and_upload_are_not_retried(mocker: MockType, call):
    mock_request = mocker.patch(
        "moneysnake.client.httpx.request",
        return_value=_response(429, headers={"Retry-After": "0"}),
    )

    with pytest.raises(MoneybirdAPIError):
        call()

    assert mock_request.call_count == 1


def test_download_follows_redirect_without_forwarding_token(mocker: MockType):
    mocker.patch.object(client, "token_", "secret-token")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.host == "moneybird.com":
            return httpx.Response(302, headers={"Location": "https://files.example.com/invoice.pdf"})
        return httpx.Response(200, content=b"%PDF-1.4")

    mocker.patch(
        "moneysnake.client.httpx.request",
        side_effect=_route_through(httpx.MockTransport(handler)),
    )

    response = http_get_raw("sales_invoices/1/download_pdf")

    assert response.content == b"%PDF-1.4"
    assert [request.url.host for request in seen] == ["moneybird.com", "files.example.com"]
    assert seen[0].headers["Authorization"] == "Bearer secret-token"
    assert "Authorization" not in seen[1].headers
