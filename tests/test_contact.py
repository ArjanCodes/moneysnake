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


def test_save_sends_only_set_fields(mocker: MockType):
    patch = mocker.patch("moneysnake.model.http_patch", return_value={"id": 1})
    Contact(id=1, company_name="New").save()

    patch.assert_called_once_with(
        "contacts/1", data={"contact": {"id": 1, "company_name": "New"}}
    )


def test_save_loaded_contact_sends_response_fields(
    mocker: MockType, contact_data: dict[str, Any]
):
    mocker.patch("moneysnake.model.http_get", return_value=contact_data)
    patch = mocker.patch("moneysnake.model.http_patch", return_value=contact_data)
    contact = Contact.find_by_id(1)
    contact.save()

    body = patch.call_args.kwargs["data"]["contact"]
    returned_fields = contact_data.keys() & Contact.model_fields.keys()
    assert body.keys() == returned_fields
    assert {k: v for k, v in body.items() if v is not None} == contact.model_dump(
        include=returned_fields, exclude_none=True
    )


def test_save_sends_null_for_field_set_to_none(mocker: MockType):
    patch = mocker.patch("moneysnake.model.http_patch", return_value={"id": 1})
    contact = Contact(id=1, company_name="Old")
    contact.company_name = None
    contact.save()

    patch.assert_called_once_with(
        "contacts/1", data={"contact": {"id": 1, "company_name": None}}
    )
