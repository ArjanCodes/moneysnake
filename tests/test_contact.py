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
    write_keys = {"custom_fields": "custom_fields_attributes"}
    assert body.keys() == {write_keys.get(k, k) for k in returned_fields}
    read_keys = {v: k for k, v in write_keys.items()}
    sent = {read_keys.get(k, k): v for k, v in body.items() if v is not None}
    assert sent == contact.model_dump(include=returned_fields, exclude_none=True)


def test_save_sends_null_for_field_set_to_none(mocker: MockType):
    patch = mocker.patch("moneysnake.model.http_patch", return_value={"id": 1})
    contact = Contact(id=1, company_name="Old")
    contact.company_name = None
    contact.save()

    patch.assert_called_once_with(
        "contacts/1", data={"contact": {"id": 1, "company_name": None}}
    )


def test_load_keeps_version(contact_data: dict[str, Any]):
    contact = Contact.model_validate(contact_data)
    assert contact.version == contact_data["version"]


def test_save_sends_custom_fields_attributes(mocker: MockType):
    mock_patch = mocker.patch("moneysnake.model.http_patch", return_value={"id": 1})
    contact = Contact(id=1, company_name="Acme")
    contact.set_custom_field(456, "some value")
    contact.save()
    sent = mock_patch.call_args[1]["data"]["contact"]
    assert sent["custom_fields_attributes"] == [{"id": 456, "value": "some value"}]
    assert "custom_fields" not in sent


def test_create_sends_custom_fields_attributes(mocker: MockType):
    mock_post = mocker.patch("moneysnake.model.http_post", return_value={"id": 1})
    contact = Contact(company_name="Acme")
    contact.set_custom_field(456, "some value")
    contact.save()
    sent = mock_post.call_args[1]["data"]["contact"]
    assert sent["custom_fields_attributes"] == [{"id": 456, "value": "some value"}]
    assert "custom_fields" not in sent
