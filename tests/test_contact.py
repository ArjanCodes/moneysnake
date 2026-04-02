from typing import Any

from pytest_mock import MockType

from moneysnake.contact import Contact


def test_find_by_customer_id(mocker: MockType, contact_data: dict[str, Any]):
    """
    Test that Contact.find_by_customer_id returns a Contact object with the correct data
    """
    mocker.patch("moneysnake.contact.http_get", return_value=contact_data)
    customer_id = "1"
    contact = Contact.find_by_customer_id(customer_id)

    assert contact.customer_id == customer_id
    assert contact.company_name == contact_data["company_name"]
    assert contact.firstname == contact_data["firstname"]
    assert contact.lastname == contact_data["lastname"]
