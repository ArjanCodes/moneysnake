import pytest
from unittest.mock import patch
from moneysnake.contact import Contact


@pytest.fixture(name="contact_data")
def fixture_contact_data():
    """
    Fixture for Moneybird contact data
    """
    return {
        "company_name": "Acme Inc",
        "address1": "123 Test St",
        "zipcode": "12345",
        "city": "Test City",
        "country": "Test Country",
        "phone": "123-456-7890",
        "customer_id": "CUST123",
        "firstname": "John",
        "lastname": "Doe",
        "email_ubl": True,
        "direct_debit": False,
        "type": "customer",
        "from_checkout": False,
    }


@patch("moneysnake.contact.post_request")
def test_find_by_customer_id(mock_post_request, contact_data):
    """
    Test that Contact.find_by_customer_id returns a Contact object with the correct data
    """
    mock_post_request.return_value = contact_data
    customer_id = "CUST123"
    contact = Contact.find_by_customer_id(customer_id)

    assert contact.customer_id == customer_id
    assert contact.company_name == contact_data["company_name"]
    assert contact.firstname == contact_data["firstname"]
    assert contact.lastname == contact_data["lastname"]
