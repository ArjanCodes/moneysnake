"""Shared test fixtures based on Moneybird OpenAPI spec response schemas."""

from typing import Any

import pytest


@pytest.fixture(name="contact_data")
def fixture_contact_data() -> dict[str, Any]:
    """Full contact response matching Moneybird OpenAPI contact_response schema."""
    return {
        "id": "433546185192506620",
        "administration_id": 123,
        "company_name": "Foobar Holding B.V.",
        "firstname": None,
        "lastname": "Appleseed",
        "address1": "Hoofdstraat 12",
        "address2": "",
        "zipcode": "1234 AB",
        "city": "Amsterdam",
        "country": "NL",
        "phone": "",
        "delivery_method": "Email",
        "customer_id": "1",
        "tax_number": "",
        "chamber_of_commerce": "",
        "bank_account": "",
        "is_trusted": False,
        "max_transfer_amount": None,
        "attention": "",
        "email": "info@example.com",
        "email_ubl": True,
        "send_invoices_to_attention": "",
        "send_invoices_to_email": "info@example.com",
        "send_estimates_to_attention": "",
        "send_estimates_to_email": "info@example.com",
        "sepa_active": False,
        "sepa_iban": "",
        "sepa_iban_account_name": "",
        "sepa_bic": "",
        "sepa_mandate_id": "",
        "sepa_mandate_date": None,
        "sepa_sequence_type": "RCUR",
        "credit_card_number": "",
        "credit_card_reference": "",
        "credit_card_type": None,
        "tax_number_validated_at": None,
        "tax_number_valid": None,
        "invoice_workflow_id": None,
        "estimate_workflow_id": None,
        "si_identifier": "",
        "si_identifier_type": None,
        "moneybird_payments_mandate": False,
        "direct_debit": False,
        "created_at": "2024-09-30T07:38:03.484Z",
        "updated_at": "2024-09-30T07:38:03.506Z",
        "version": 1727681883,
        "sales_invoices_url": "https://moneybird.dev/123/sales_invoices/1d1fc7ae5988bacb0cf87720826a63571db2db3756fa9d8770a27cf99f89df8b/all",
        "archived": False,
        "notes": [],
        "custom_fields": [],
        "contact_people": [
            {
                "id": "433546185198798078",
                "contact_id": "433546185192506620",
                "administration_id": 123,
                "firstname": "John",
                "lastname": "Appleseed",
                "phone": None,
                "email": None,
                "department": None,
                "created_at": "2024-09-30T07:38:03.491Z",
                "updated_at": "2024-09-30T07:38:03.491Z",
                "version": 1727681883,
            }
        ],
        "events": [
            {
                "administration_id": 123,
                "user_id": 1727681857838,
                "action": "contact_created",
                "link_entity_id": None,
                "link_entity_type": None,
                "data": {},
                "created_at": "2024-09-30T07:38:03.498Z",
                "updated_at": "2024-09-30T07:38:03.498Z",
            }
        ],
    }


@pytest.fixture(name="payment_data")
def fixture_payment_data() -> dict[str, Any]:
    """Full payment response matching Moneybird OpenAPI payment_response schema."""
    return {
        "id": "433546310070568441",
        "administration_id": 123,
        "invoice_type": "SalesInvoice",
        "invoice_id": "433546309874484716",
        "financial_account_id": "433546310057985525",
        "user_id": 1727681857838,
        "payment_transaction_id": None,
        "transaction_identifier": None,
        "price": "363.0",
        "price_base": "363.0",
        "payment_date": "2024-09-30",
        "credit_invoice_id": None,
        "financial_mutation_id": "433546310065325560",
        "ledger_account_id": "433546310050645492",
        "linked_payment_id": None,
        "manual_payment_action": "bank_transfer",
        "created_at": "2024-09-30T07:40:02.576Z",
        "updated_at": "2024-09-30T07:40:02.576Z",
    }
