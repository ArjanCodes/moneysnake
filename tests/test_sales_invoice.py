from typing import Any

import pytest
from pytest_mock import MockType

from moneysnake.payment import Payment
from moneysnake.sales_invoice import (
    SalesInvoice,
    SalesInvoiceDetailsAttribute,
)


@pytest.fixture(name="invoice_data")
def fixture_invoice_data() -> dict[str, Any]:
    return {
        "id": "550000000000000001",
        "administration_id": 123,
        "contact_id": "550000000000000002",
        "contact_person_id": None,
        "invoice_id": "2026-0001",
        "workflow_id": "550000000000000010",
        "document_style_id": "550000000000000011",
        "identity_id": "550000000000000012",
        "draft_id": None,
        "state": "draft",
        "paused": False,
        "invoice_date": "2026-03-31",
        "due_date": "2026-04-30",
        "payment_conditions": "Net 30",
        "payment_reference": None,
        "short_payment_reference": None,
        "reference": "Project Alpha",
        "language": "nl",
        "currency": "EUR",
        "discount": None,
        "prices_are_incl_tax": False,
        "total_paid": "0.0",
        "total_unpaid": "121.0",
        "total_unpaid_base": "121.0",
        "total_price_excl_tax": "100.0",
        "total_price_excl_tax_base": "100.0",
        "total_price_incl_tax": "121.0",
        "total_price_incl_tax_base": "121.0",
        "total_discount": "0.0",
        "paid_at": None,
        "sent_at": None,
        "created_at": "2026-03-31T10:00:00.000Z",
        "updated_at": "2026-03-31T10:00:00.000Z",
        "version": 1711872000,
        "url": "https://moneybird.com/123/sales_invoices/abc123",
        "payment_url": "https://moneybird.com/pay/abc123",
        "public_view_code": "abc123",
        "marked_dubious_on": None,
        "marked_uncollectible_on": None,
        "reminder_count": 0,
        "next_reminder": None,
        "original_estimate_id": None,
        "recurring_sales_invoice_id": None,
        "subscription_id": None,
        "details": [
            {
                "id": "550000000000000100",
                "description": "Consulting services",
                "period": None,
                "price": "100.0",
                "amount": "1 x",
                "tax_rate_id": "550000000000000200",
                "ledger_account_id": "550000000000000201",
                "project_id": None,
                "product_id": None,
                "row_order": 0,
            }
        ],
        "payments": [],
        "tax_totals": [
            {
                "tax_rate_id": "550000000000000200",
                "taxable_amount": "100.0",
                "tax_amount": "21.0",
            }
        ],
        "custom_fields": [],
        "notes": [],
        "attachments": [],
        "events": [],
    }


@pytest.fixture(name="payment_data")
def fixture_payment_data() -> dict[str, Any]:
    return {
        "id": "550000000000000300",
        "administration_id": 123,
        "invoice_type": "SalesInvoice",
        "invoice_id": "550000000000000001",
        "financial_account_id": None,
        "user_id": 999,
        "payment_transaction_id": None,
        "transaction_identifier": None,
        "price": "121.0",
        "price_base": "121.0",
        "payment_date": "2026-03-31",
        "credit_invoice_id": None,
        "financial_mutation_id": None,
        "ledger_account_id": "550000000000000400",
        "linked_payment_id": None,
        "manual_payment_action": "bank_transfer",
        "created_at": "2026-03-31T10:00:00.000Z",
        "updated_at": "2026-03-31T10:00:00.000Z",
    }


# --- CRUD tests ---


def test_save_new_invoice(mocker: MockType, invoice_data: dict[str, Any]):
    del invoice_data["id"]
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {"id": 550000000000000001, **invoice_data}
    invoice = SalesInvoice(**invoice_data)
    invoice.save()
    assert invoice.id == 550000000000000001
    call_data = mock_post.call_args[1]["data"]["sales_invoice"]
    assert "details_attributes" in call_data
    assert "details" not in call_data


def test_update_existing_invoice(mocker: MockType, invoice_data: dict[str, Any]):
    mock_patch = mocker.patch("moneysnake.sales_invoice.http_patch")
    mock_patch.return_value = invoice_data
    invoice = SalesInvoice(**invoice_data)
    invoice.save()
    assert invoice.id is not None


def test_find_by_id(mocker: MockType, invoice_data: dict[str, Any]):
    mocker.patch("moneysnake.model.http_get", return_value=invoice_data)
    invoice = SalesInvoice.find_by_id(550000000000000001)
    assert invoice.invoice_id == "2026-0001"
    assert invoice.state == "draft"


def test_delete(mocker: MockType, invoice_data: dict[str, Any]):
    mock_delete = mocker.patch("moneysnake.model.http_delete")
    invoice = SalesInvoice(**invoice_data)
    invoice.delete()
    assert invoice.id is None
    mock_delete.assert_called_once()


def test_update_by_id(mocker: MockType, invoice_data: dict[str, Any]):
    mock_patch = mocker.patch("moneysnake.sales_invoice.http_patch")
    mock_patch.return_value = {**invoice_data, "reference": "Updated"}
    invoice = SalesInvoice.update_by_id(550000000000000001, {"reference": "Updated"})
    assert invoice.reference == "Updated"


# --- Detail management ---


def test_add_detail(invoice_data: dict[str, Any]):
    invoice = SalesInvoice(**invoice_data)
    detail = SalesInvoiceDetailsAttribute(description="New item", price="50.0", amount="2")
    invoice.add_detail(detail)
    assert len(invoice.details) == 2


def test_get_detail(invoice_data: dict[str, Any]):
    invoice = SalesInvoice(**invoice_data)
    detail = invoice.get_detail(550000000000000100)
    assert detail.description == "Consulting services"


def test_get_detail_not_found(invoice_data: dict[str, Any]):
    invoice = SalesInvoice(**invoice_data)
    with pytest.raises(ValueError, match="not found"):
        invoice.get_detail(999)


def test_update_detail(invoice_data: dict[str, Any]):
    invoice = SalesInvoice(**invoice_data)
    detail = invoice.update_detail(550000000000000100, {"description": "Updated"})
    assert detail.description == "Updated"


def test_delete_detail(invoice_data: dict[str, Any]):
    invoice = SalesInvoice(**invoice_data)
    invoice.delete_detail(550000000000000100)
    assert len(invoice.details) == 0


# --- Payment management ---


def test_create_payment(
    mocker: MockType, invoice_data: dict[str, Any], payment_data: dict[str, Any]
):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {"payment": payment_data}
    invoice = SalesInvoice(**invoice_data)
    invoice.create_payment(Payment(**payment_data))
    assert len(invoice.payments) == 1
    assert invoice.payments[0].id == 550000000000000300


def test_delete_payment(
    mocker: MockType, invoice_data: dict[str, Any], payment_data: dict[str, Any]
):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {"payment": payment_data}
    invoice = SalesInvoice(**invoice_data)
    invoice.create_payment(Payment(**payment_data))

    mock_delete = mocker.patch("moneysnake.sales_invoice.http_delete")
    invoice.delete_payment(550000000000000300)
    assert len(invoice.payments) == 0
    mock_delete.assert_called_once()


# --- Actions ---


def test_send_invoice(mocker: MockType, invoice_data: dict[str, Any]):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {**invoice_data, "state": "open", "sent_at": "2026-03-31"}
    invoice = SalesInvoice(**invoice_data)
    invoice.send_invoice(delivery_method="Email")
    assert invoice.state == "open"
    call_data = mock_post.call_args[1]["data"]
    assert call_data["sales_invoice_sending"]["delivery_method"] == "Email"


def test_send_invoice_no_options(mocker: MockType, invoice_data: dict[str, Any]):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {**invoice_data, "state": "open"}
    invoice = SalesInvoice(**invoice_data)
    invoice.send_invoice()
    assert mock_post.call_args[1]["data"] is None


def test_pause(mocker: MockType, invoice_data: dict[str, Any]):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {**invoice_data, "paused": True}
    invoice = SalesInvoice(**invoice_data)
    invoice.pause()
    assert invoice.paused is True


def test_resume(mocker: MockType, invoice_data: dict[str, Any]):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    invoice_data["paused"] = True
    mock_post.return_value = {**invoice_data, "paused": False}
    invoice = SalesInvoice(**invoice_data)
    invoice.resume()
    assert invoice.paused is False


def test_mark_as_dubious(mocker: MockType, invoice_data: dict[str, Any]):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {**invoice_data, "marked_dubious_on": "2026-03-31"}
    invoice = SalesInvoice(**invoice_data)
    invoice.mark_as_dubious()
    assert invoice.marked_dubious_on == "2026-03-31"


def test_mark_as_uncollectible(mocker: MockType, invoice_data: dict[str, Any]):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {**invoice_data, "marked_uncollectible_on": "2026-03-31"}
    invoice = SalesInvoice(**invoice_data)
    invoice.mark_as_uncollectible()
    assert invoice.marked_uncollectible_on == "2026-03-31"


def test_duplicate_creditinvoice(mocker: MockType, invoice_data: dict[str, Any]):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    credit_data = {**invoice_data, "id": "550000000000000999", "state": "draft"}
    mock_post.return_value = credit_data
    invoice = SalesInvoice(**invoice_data)
    credit = invoice.duplicate_creditinvoice()
    assert credit.id == 550000000000000999
    assert credit.id != invoice.id


def test_register_payment(
    mocker: MockType, invoice_data: dict[str, Any], payment_data: dict[str, Any]
):
    mock_post = mocker.patch("moneysnake.sales_invoice.http_post")
    mock_post.return_value = {**invoice_data, "state": "paid", "paid_at": "2026-03-31"}
    invoice = SalesInvoice(**invoice_data)
    invoice.register_payment(Payment(**payment_data))
    assert invoice.state == "paid"


def test_download_pdf(mocker: MockType, invoice_data: dict[str, Any]):
    mock_get = mocker.patch("moneysnake.sales_invoice.http_get")
    mock_get.return_value = b"%PDF-1.4"
    invoice = SalesInvoice(**invoice_data)
    result = invoice.download_pdf()
    assert result == b"%PDF-1.4"
    mock_get.assert_called_once_with("sales_invoices/550000000000000001/download_pdf")


def test_download_ubl(mocker: MockType, invoice_data: dict[str, Any]):
    mock_get = mocker.patch("moneysnake.sales_invoice.http_get")
    mock_get.return_value = "<xml>ubl</xml>"
    invoice = SalesInvoice(**invoice_data)
    result = invoice.download_ubl()
    assert result == "<xml>ubl</xml>"


# --- Lookup helpers ---


def test_list_all(mocker: MockType, invoice_data: dict[str, Any]):
    mock_paginate = mocker.patch("moneysnake.sales_invoice.paginate")
    mock_paginate.return_value = [invoice_data, invoice_data]
    invoices = SalesInvoice.list_all(state="open", period="this_year")
    assert len(invoices) == 2
    call_params = mock_paginate.call_args[1]["params"]
    assert "state:open" in call_params["filter"]
    assert "period:this_year" in call_params["filter"]


def test_list_all_no_filters(mocker: MockType, invoice_data: dict[str, Any]):
    mock_paginate = mocker.patch("moneysnake.sales_invoice.paginate")
    mock_paginate.return_value = [invoice_data]
    invoices = SalesInvoice.list_all()
    assert len(invoices) == 1
    mock_paginate.assert_called_once_with("sales_invoices", params=None)


def test_find_by_invoice_id(mocker: MockType, invoice_data: dict[str, Any]):
    mock_get = mocker.patch("moneysnake.sales_invoice.http_get")
    mock_get.return_value = invoice_data
    invoice = SalesInvoice.find_by_invoice_id("2026-0001")
    assert invoice.invoice_id == "2026-0001"
    mock_get.assert_called_once_with("sales_invoices/find_by_invoice_id/2026-0001")


def test_find_by_reference(mocker: MockType, invoice_data: dict[str, Any]):
    mock_get = mocker.patch("moneysnake.sales_invoice.http_get")
    mock_get.return_value = invoice_data
    invoice = SalesInvoice.find_by_reference("Project Alpha")
    assert invoice.reference == "Project Alpha"


# --- Field validators ---


def test_payments_converted_from_dicts(mocker: MockType, invoice_data: dict[str, Any], payment_data: dict[str, Any]):
    invoice_data["payments"] = [payment_data]
    mocker.patch("moneysnake.model.http_get", return_value=invoice_data)
    invoice = SalesInvoice.find_by_id(550000000000000001)
    assert len(invoice.payments) == 1
    assert isinstance(invoice.payments[0], Payment)


def test_details_converted_from_dicts(invoice_data: dict[str, Any]):
    invoice = SalesInvoice(**invoice_data)
    assert len(invoice.details) == 1
    assert isinstance(invoice.details[0], SalesInvoiceDetailsAttribute)


def test_endpoint_is_sales_invoice():
    invoice = SalesInvoice()
    assert invoice.endpoint == "sales_invoice"
