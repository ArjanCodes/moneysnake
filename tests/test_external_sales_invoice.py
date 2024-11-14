import pytest
from unittest.mock import patch
from moneysnake.external_sales_invoice import (
    ExternalSalesInvoice,
)


@pytest.fixture(name="invoice_data")
def fixture_invoice_data():
    """
    Return a dictionary with data for an external sales invoice.
    """
    return {
        "id": "433546255183906622",
        "administration_id": 123,
        "contact_id": "433546255117846332",
        "contact": {
            "id": "433546255117846332",
            "administration_id": 123,
            "company_name": "Relation 2",
            "firstname": None,
            "lastname": None,
            "address1": None,
            "address2": None,
            "zipcode": None,
            "city": None,
            "country": "NL",
            "phone": None,
            "delivery_method": "Email",
            "customer_id": "485af44c484c6ef966d2eaa8c974889aafed1cb05fb755974f13d7baf43aa01a",
            "tax_number": "BE0464995729",
            "chamber_of_commerce": None,
            "bank_account": None,
            "is_trusted": False,
            "max_transfer_amount": None,
            "attention": None,
            "email": "invoices@example.com",
            "email_ubl": False,
            "send_invoices_to_attention": None,
            "send_invoices_to_email": "invoices@example.com",
            "send_estimates_to_attention": None,
            "send_estimates_to_email": "estimates@example.com",
            "sepa_active": False,
            "sepa_iban": None,
            "sepa_iban_account_name": None,
            "sepa_bic": None,
            "sepa_mandate_id": None,
            "sepa_mandate_date": None,
            "sepa_sequence_type": "RCUR",
            "credit_card_number": None,
            "credit_card_reference": None,
            "credit_card_type": None,
            "tax_number_validated_at": "2024-09-30T07:39:10.167Z",
            "tax_number_valid": True,
            "invoice_workflow_id": None,
            "estimate_workflow_id": None,
            "si_identifier": None,
            "si_identifier_type": None,
            "moneybird_payments_mandate": False,
            "created_at": "2024-09-30T07:39:10.170Z",
            "updated_at": "2024-09-30T07:39:10.170Z",
            "version": 1727681950,
            "sales_invoices_url": "https://moneybird.dev/123/sales_invoices/887fa17796b69b04972b56b7c39899055c13716b4fe279f7ea3fc48e5c3f5fc5/all",
            "notes": [],
            "custom_fields": [],
            "contact_people": [],
            "archived": False,
        },
        "date": "2024-09-30",
        "state": "open",
        "due_date": None,
        "reference": "30052",
        "entry_number": 1,
        "origin": "api",
        "source": None,
        "source_url": None,
        "currency": "EUR",
        "paid_at": None,
        "created_at": "2024-09-30T07:39:10.234Z",
        "updated_at": "2024-09-30T07:39:10.237Z",
        "version": 1727681950,
        "details": [
            {
                "id": "433546255186003775",
                "administration_id": 123,
                "tax_rate_id": "433546158515685191",
                "ledger_account_id": "433546158461159223",
                "project_id": None,
                "product_id": None,
                "amount": None,
                "amount_decimal": "1.0",
                "description": "Rocking Chair",
                "price": "129.95",
                "period": None,
                "row_order": 0,
                "total_price_excl_tax_with_discount": "129.95",
                "total_price_excl_tax_with_discount_base": "129.95",
                "tax_report_reference": ["NL/1a"],
                "mandatory_tax_text": None,
                "created_at": "2024-09-30T07:39:10.235Z",
                "updated_at": "2024-09-30T07:39:10.235Z",
            }
        ],
        "payments": [],
        "total_paid": "0.0",
        "total_unpaid": "157.24",
        "total_unpaid_base": "157.24",
        "prices_are_incl_tax": False,
        "total_price_excl_tax": "129.95",
        "total_price_excl_tax_base": "129.95",
        "total_price_incl_tax": "157.24",
        "total_price_incl_tax_base": "157.24",
        "marked_dubious_on": None,
        "marked_uncollectible_on": None,
        "notes": [],
        "attachments": [],
        "events": [
            {
                "administration_id": 123,
                "user_id": 1727681857838,
                "action": "external_sales_invoice_created",
                "link_entity_id": None,
                "link_entity_type": None,
                "data": {},
                "created_at": "2024-09-30T07:39:10.238Z",
                "updated_at": "2024-09-30T07:39:10.238Z",
            }
        ],
        "tax_totals": [
            {
                "tax_rate_id": "433546158515685191",
                "taxable_amount": "129.95",
                "taxable_amount_base": "129.95",
                "tax_amount": "27.29",
                "tax_amount_base": "27.29",
            }
        ],
    }


@pytest.fixture(name="payment_data")
def fixture_payment_data():
    """
    Return a dictionary with data for an external sales invoice payment.
    """
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


@patch("moneysnake.external_sales_invoice.post_request")
def test_save_new_invoice(mock_post_request, invoice_data):
    """
    Test saving a new external sales invoice.
    """
    mock_post_request.return_value = {**invoice_data}
    invoice = ExternalSalesInvoice(**invoice_data)
    invoice.save()
    assert invoice.id == 433546255183906622


@patch("moneysnake.external_sales_invoice.post_request")
def test_update_existing_invoice(mock_post_request, invoice_data):
    """
    Test updating an existing external sales invoice.
    """
    invoice_data["id"] = 433546255183906622
    mock_post_request.return_value = invoice_data
    invoice = ExternalSalesInvoice(**invoice_data)
    invoice.save()
    assert invoice.id == 433546255183906622


@patch("moneysnake.external_sales_invoice.post_request")
def test_create_payment(mock_post_request, invoice_data, payment_data):
    """
    Test creating a payment for an external sales invoice.
    """
    mock_post_request.return_value = {"payment": payment_data}
    invoice = ExternalSalesInvoice(**invoice_data)
    invoice.id = 433546255183906622
    payment = invoice.create_payment(payment_data)
    assert payment.price == payment_data.price


@patch("moneysnake.external_sales_invoice.post_request")
def test_update_by_id(mock_post_request, invoice_data):
    """
    Test updating an external sales invoice by ID.
    """
    mock_post_request.return_value = {**invoice_data}
    updated_data = {"date": "2024-09-29"}
    invoice = ExternalSalesInvoice.update_by_id(433546255183906622, updated_data)
    assert invoice.date == "2024-09-29"
