import pytest
from pytest_mock import MockType
from moneysnake.contact import Contact

type ContactData = dict[
    str,
    str
    | int
    | bool
    | None
    | list[
        dict[str, str | int | bool | None | dict[str, str]]
        | dict[str, str | int | bool | None]
    ],
]


@pytest.fixture(name="contact_data")
def fixture_contact_data() -> ContactData:
    """
    Fixture for Moneybird contact data
    """
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
        "created_at": "2024-09-30T07:38:03.484Z",
        "updated_at": "2024-09-30T07:38:03.506Z",
        "version": 1727681883,
        "sales_invoices_url": "https://moneybird.dev/123/sales_invoices/1d1fc7ae5988bacb0cf87720826a63571db2db3756fa9d8770a27cf99f89df8b/all",
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
        "archived": False,
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


def test_find_by_customer_id(mocker: MockType, contact_data: ContactData):
    """
    Test that Contact.find_by_customer_id returns a Contact object with the correct data
    """
    mocker.patch("moneysnake.contact.post_request", return_value=contact_data)
    customer_id = "1"
    contact = Contact.find_by_customer_id(customer_id)

    assert contact.customer_id == customer_id
    assert contact.company_name == contact_data["company_name"]
    assert contact.firstname == contact_data["firstname"]
    assert contact.lastname == contact_data["lastname"]
