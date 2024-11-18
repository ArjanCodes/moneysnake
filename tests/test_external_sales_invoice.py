import pytest
from unittest.mock import patch
from moneysnake.external_sales_invoice import ExternalSalesInvoice


@pytest.fixture(name="invoice_data")
def fixture_invoice_data():
    """
    Return a dictionary with data for an external sales invoice.
    """
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
            "credit_card_number": None,
            "credit_card_reference": None,
            "credit_card_type": None,
            "tax_number_validated_at": None,
            "tax_number_valid": None,
            "invoice_workflow_id": None,
            "estimate_workflow_id": None,
            "si_identifier": None,
            "si_identifier_type": None,
            "moneybird_payments_mandate": False,
            "created_at": "2024-09-30T07:39:09.921Z",
            "updated_at": "2024-09-30T07:39:09.921Z",
            "version": 1727681949,
            "sales_invoices_url": "https://moneybird.dev/123/sales_invoices/0e44bc63682a3ea5a870f0aec22984691c4ff8344cdd0bffac7eb11270216789/all",
            "notes": [],
            "custom_fields": [],
            "contact_people": [],
            "archived": False,
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
    # Remove id from invoice data
    del invoice_data["id"]
    mock_post_request.return_value = {"id": "433546255183906622", **invoice_data}
    invoice = ExternalSalesInvoice.from_dict(invoice_data)
    invoice.save()
    assert invoice.id == "433546255183906622"


@patch("moneysnake.external_sales_invoice.post_request")
def test_update_existing_invoice(mock_post_request, invoice_data):
    """
    Test updating an existing external sales invoice.
    """
    mock_post_request.return_value = invoice_data
    invoice = ExternalSalesInvoice.from_dict(invoice_data)
    invoice.save()
    assert invoice.id == "433546254874576683"


@patch("moneysnake.external_sales_invoice.post_request")
def test_create_payment(mock_post_request, invoice_data, payment_data):
    """
    Test creating a payment for an external sales invoice.
    """
    mock_post_request.return_value = {"payment": payment_data}
    invoice = ExternalSalesInvoice.from_dict(invoice_data)
    invoice.id = 433546254874576683
    payment = invoice.create_payment(payment_data)

    assert payment.price == payment_data.get("price")


@patch("moneysnake.external_sales_invoice.post_request")
def test_update_by_id(mock_post_request, invoice_data):
    """
    Test updating an external sales invoice by ID.
    """
    mock_post_request.return_value = {"id": 433546254874576683, **invoice_data}
    updated_data = {"date": "2024-09-29"}
    invoice = ExternalSalesInvoice.update_by_id(433546254874576683, updated_data)
    assert invoice.date == "2024-09-29"
