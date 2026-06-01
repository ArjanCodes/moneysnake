from typing import Any

import pytest
from pytest_mock import MockType

from moneysnake.external_sales_invoice import (
    ExternalSalesInvoice,
    ExternalSalesInvoiceDetailsAttribute,
)
from moneysnake.payment import Payment as ExternalSalesInvoicePayment


@pytest.fixture(name="ext_invoice_data")
def fixture_ext_invoice_data() -> dict[str, Any]:
    """Full external sales invoice response matching Moneybird OpenAPI
    external_sales_invoice_response schema."""
    return {
        "id": "433546254874576683",
        "administration_id": 123,
        "contact_id": "433546254856750888",
        "contact": {
            "id": "433546254856750888",
            "administration_id": 123,
            "company_name": "Relation 1",
            "firstname": None,
            "lastname": None,
            "address1": None,
            "address2": None,
            "zipcode": None,
            "city": None,
            "country": "NL",
            "phone": None,
            "delivery_method": "Email",
            "customer_id": "664461b3ecd23cfa7769dafcd5e333691e812c5fc9ccde92283907cf9c95a1f7",
            "tax_number": None,
            "chamber_of_commerce": None,
            "bank_account": None,
            "is_trusted": False,
            "max_transfer_amount": None,
            "attention": None,
            "email": None,
            "email_ubl": False,
            "send_invoices_to_attention": None,
            "send_invoices_to_email": None,
            "send_estimates_to_attention": None,
            "send_estimates_to_email": None,
            "sepa_active": False,
            "sepa_iban": None,
            "sepa_iban_account_name": None,
            "sepa_bic": None,
            "sepa_mandate_id": None,
            "sepa_mandate_date": None,
            "sepa_sequence_type": "RCUR",
            "si_identifier": None,
            "si_identifier_type": None,
            "created_at": "2024-09-30T07:39:09.921Z",
            "updated_at": "2024-09-30T07:39:09.921Z",
            "version": 1727681949,
        },
        "date": "2024-09-30",
        "state": "open",
        "due_date": None,
        "reference": "Invoice 1",
        "entry_number": 101,
        "origin": None,
        "source": None,
        "source_url": None,
        "currency": "EUR",
        "paid_at": None,
        "created_at": "2024-09-30T07:39:09.939Z",
        "updated_at": "2024-09-30T07:39:09.943Z",
        "version": 1727681949,
        "details": [
            {
                "id": "433546254876673836",
                "administration_id": 123,
                "tax_rate_id": "433546254866188074",
                "ledger_account_id": "433546254863042345",
                "project_id": None,
                "product_id": None,
                "amount": "1 x",
                "amount_decimal": "1.0",
                "description": "Invoice detail description",
                "price": "100.0",
                "period": None,
                "row_order": 0,
                "total_price_excl_tax_with_discount": "100.0",
                "total_price_excl_tax_with_discount_base": "100.0",
                "tax_report_reference": [],
                "mandatory_tax_text": None,
                "created_at": "2024-09-30T07:39:09.941Z",
                "updated_at": "2024-09-30T07:39:09.941Z",
            }
        ],
        "payments": [],
        "total_paid": "0.0",
        "total_unpaid": "121.0",
        "total_unpaid_base": "121.0",
        "prices_are_incl_tax": False,
        "total_price_excl_tax": "100.0",
        "total_price_excl_tax_base": "100.0",
        "total_price_incl_tax": "121.0",
        "total_price_incl_tax_base": "121.0",
        "marked_dubious_on": None,
        "marked_uncollectible_on": None,
        "notes": [],
        "attachments": [],
        "events": [],
        "tax_totals": [
            {
                "tax_rate_id": "433546254866188074",
                "taxable_amount": "100.0",
                "taxable_amount_base": "100.0",
                "tax_amount": "21.0",
                "tax_amount_base": "21.0",
            }
        ],
    }


@pytest.fixture(name="ext_payment_data")
def fixture_ext_payment_data() -> dict[str, Any]:
    """Payment response for an external sales invoice."""
    return {
        "id": "433546259519768528",
        "administration_id": 123,
        "invoice_type": "ExternalSalesInvoice",
        "invoice_id": "433546259464193998",
        "financial_account_id": None,
        "user_id": 1727681857838,
        "payment_transaction_id": None,
        "transaction_identifier": None,
        "price": "121.0",
        "price_base": "121.0",
        "payment_date": "2024-09-30",
        "credit_invoice_id": None,
        "financial_mutation_id": None,
        "ledger_account_id": "433546158492616512",
        "linked_payment_id": None,
        "manual_payment_action": None,
        "created_at": "2024-09-30T07:39:14.368Z",
        "updated_at": "2024-09-30T07:39:14.368Z",
    }


def test_save_new_invoice(mocker: MockType, ext_invoice_data: dict[str, Any]):
    """
    Test saving a new external sales invoice.
    """
    del ext_invoice_data["id"]
    mock_make_request = mocker.patch("moneysnake.external_sales_invoice.http_post")
    mock_make_request.return_value = {"id": 433546255183906622, **ext_invoice_data}
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.save()
    assert invoice.id == 433546255183906622


def test_update_existing_invoice(mocker: MockType, ext_invoice_data: dict[str, Any]):
    """
    Test updating an existing external sales invoice.
    """
    mock_make_request = mocker.patch("moneysnake.external_sales_invoice.http_patch")
    mock_make_request.return_value = ext_invoice_data
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.save()

    assert invoice.id is not None
    assert int(invoice.id) == 433546254874576683


def test_create_payment(
    mocker: MockType,
    ext_invoice_data: dict[str, Any],
    ext_payment_data: dict[str, Any],
):
    """
    Test creating a payment for an external sales invoice.
    """
    mock_make_request = mocker.patch("moneysnake.external_sales_invoice.http_post")
    mock_make_request.return_value = {"payment": ext_payment_data}
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.id = 433546254874576683
    external_sales_invoice_payment = ExternalSalesInvoicePayment(**ext_payment_data)
    created = invoice.create_payment(external_sales_invoice_payment)

    assert invoice.payments is not None
    assert len(invoice.payments) == 1
    assert created is invoice.payments[-1]


def test_create_payment_unwrapped_response(
    mocker: MockType,
    ext_invoice_data: dict[str, Any],
    ext_payment_data: dict[str, Any],
):
    """Moneybird returns the payment fields at the top level (no wrapper)."""
    mock_make_request = mocker.patch("moneysnake.external_sales_invoice.http_post")
    mock_make_request.return_value = ext_payment_data
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.id = 433546254874576683
    created = invoice.create_payment(ExternalSalesInvoicePayment(**ext_payment_data))

    assert len(invoice.payments) == 1
    assert created.id == int(ext_payment_data["id"])


def test_delete_payment(
    mocker: MockType,
    ext_invoice_data: dict[str, Any],
    ext_payment_data: dict[str, Any],
):
    """
    Test deleting a payment for an external sales invoice.
    """
    mock_make_request = mocker.patch("moneysnake.external_sales_invoice.http_post")

    mock_make_request.return_value = {"payment": ext_payment_data}
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.id = 433546254874576683
    invoice.create_payment(ExternalSalesInvoicePayment(**ext_payment_data))

    assert invoice.payments is not None

    assert len(invoice.payments) == 1

    mock_make_request = mocker.patch("moneysnake.external_sales_invoice.http_delete")
    mock_make_request.return_value = None
    invoice.delete_payment(433546259519768528)

    assert len(invoice.payments) == 0


def test_list_all_by_contact_id(mocker: MockType, ext_invoice_data: dict[str, Any]):
    """
    Test listing all external sales invoices for a contact.
    """
    mock_paginate = mocker.patch("moneysnake.external_sales_invoice.paginate")
    mock_paginate.return_value = [ext_invoice_data]
    invoices = ExternalSalesInvoice().list_all_by_contact_id(433546254856750888)
    assert len(invoices) == 1


def test_update_by_id(mocker: MockType, ext_invoice_data: dict[str, Any]):
    """
    Test updating an external sales invoice by ID.
    """
    mock_make_request = mocker.patch("moneysnake.external_sales_invoice.http_patch")
    mock_make_request.return_value = {**ext_invoice_data, "date": "2024-09-29"}
    updated_data = {"date": "2024-09-29"}
    invoice = ExternalSalesInvoice.update_by_id(433546254874576683, updated_data)
    assert invoice.date == "2024-09-29"


def test_add_detail(ext_invoice_data: dict[str, Any]):
    """
    Test adding a detail to an external sales invoice.
    """
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    detail_data: dict[str, Any] = {
        "id": 2,
        "description": "New detail",
        "price": 200,
        "amount": 2,
    }
    detail = ExternalSalesInvoiceDetailsAttribute(**detail_data)
    invoice.add_detail(detail)

    assert invoice.details is not None

    assert len(invoice.details) == 2
    assert invoice.details[-1].description == "New detail"


def test_get_detail(ext_invoice_data: dict[str, Any]):
    """
    Test getting a detail from an external sales invoice.
    """
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    detail = invoice.get_detail(433546254876673836)
    assert detail.description == "Invoice detail description"


def test_update_detail(ext_invoice_data: dict[str, Any]):
    """
    Test updating a detail from an external sales invoice.
    """
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    updated_detail_data = ExternalSalesInvoiceDetailsAttribute(
        description="Updated description"
    ).model_dump(exclude_none=True)
    detail = invoice.update_detail(433546254876673836, updated_detail_data)
    assert detail.description == "Updated description"


def test_delete_detail(ext_invoice_data: dict[str, Any]):
    """
    Test deleting a detail from an external sales invoice.
    """
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.delete_detail(433546254876673836)
    assert invoice.details is not None
    assert len(invoice.details) == 0


def test_delete_detail_not_found(ext_invoice_data: dict[str, Any]):
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    with pytest.raises(ValueError, match="not found"):
        invoice.delete_detail(999)


def test_delete_detail_sends_destroy_on_save(
    mocker: MockType, ext_invoice_data: dict[str, Any]
):
    mock_patch = mocker.patch("moneysnake.external_sales_invoice.http_patch")
    mock_patch.return_value = {**ext_invoice_data, "details": []}
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.delete_detail(433546254876673836)
    invoice.save()

    sent = mock_patch.call_args[1]["data"]["external_sales_invoice"][
        "details_attributes"
    ]
    assert {"id": 433546254876673836, "_destroy": True} in sent
    assert invoice._destroyed_detail_ids == []


def test_delete_detail_destroy_kept_after_failed_save(
    mocker: MockType, ext_invoice_data: dict[str, Any]
):
    mocker.patch(
        "moneysnake.external_sales_invoice.http_patch",
        side_effect=RuntimeError("boom"),
    )
    invoice = ExternalSalesInvoice(**ext_invoice_data)
    invoice.delete_detail(433546254876673836)
    with pytest.raises(RuntimeError):
        invoice.save()
    assert invoice._destroyed_detail_ids == [433546254876673836]


def test_find_by_id_converts_payments_to_objects(
    mocker: MockType,
    ext_invoice_data: dict[str, Any],
    ext_payment_data: dict[str, Any],
):
    """
    Test that find_by_id properly converts payment dicts to Payment objects.
    This tests that the update method runs field validators.
    """
    ext_invoice_data["payments"] = [ext_payment_data]

    mock_http_get = mocker.patch(
        "moneysnake.model.http_get", return_value=ext_invoice_data
    )

    invoice = ExternalSalesInvoice.find_by_id(433546254874576683)

    mock_http_get.assert_called_once()
    assert invoice.payments is not None
    assert len(invoice.payments) == 1
    assert isinstance(invoice.payments[0], ExternalSalesInvoicePayment)
    assert invoice.payments[0].id == 433546259519768528


def test_load_converts_payments_to_objects(
    mocker: MockType,
    ext_invoice_data: dict[str, Any],
    ext_payment_data: dict[str, Any],
):
    """
    Test that load properly converts payment dicts to Payment objects.
    """
    ext_invoice_data["payments"] = [ext_payment_data]

    mocker.patch("moneysnake.model.http_get", return_value=ext_invoice_data)

    invoice = ExternalSalesInvoice(id=433546254874576683)
    invoice.load(433546254874576683)

    assert invoice.payments is not None
    assert len(invoice.payments) == 1
    assert isinstance(invoice.payments[0], ExternalSalesInvoicePayment)
    assert invoice.payments[0].id == 433546259519768528
