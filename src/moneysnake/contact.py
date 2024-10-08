from typing import Any, Optional

from client import post_request
from custom_field import CustomField
from pydantic import BaseModel


class ContactPerson(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None


class Contact(BaseModel):
    id: Optional[int] = None
    company_name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    zipcode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    delivery_method: Optional[str] = None
    customer_id: Optional[str] = None
    tax_number: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    chamber_of_commerce: Optional[str] = None
    bank_account: Optional[str] = None
    send_invoices_to_attention: Optional[str] = None
    send_invoices_to_email: Optional[str] = None
    send_estimates_to_attention: Optional[str] = None
    send_estimates_to_email: Optional[str] = None
    sepa_active: bool = False
    sepa_iban: Optional[str] = None
    sepa_iban_account_name: Optional[str] = None
    sepa_bic: Optional[str] = None
    sepa_mandate_id: Optional[str] = None
    sepa_mandate_date: Optional[str] = None
    sepa_sequence_type: Optional[str] = None
    si_identifier_type: Optional[str] = None
    si_identifier: Optional[str] = None
    invoice_workflow_id: Optional[int] = None
    estimate_workflow_id: Optional[int] = None
    email_ubl: bool = False
    direct_debit: bool = False
    contact_person: Optional[ContactPerson] = None
    custom_fields: list[CustomField] = []
    type: Optional[str] = None
    from_checkout: bool = False

    def get_custom_field(self, field_id: int) -> str | None:
        for field in self.custom_fields:
            if field.id == field_id:
                return field.value
        return None

    def set_custom_field(self, field_id: int, value: str) -> None:
        for field in self.custom_fields:
            if field.id == field_id:
                field.value = value
                return
        self.custom_fields.append(CustomField(id=field_id, value=value))

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Contact":
        return Contact(**data)

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def delete(self) -> "Contact":
        if not self.id:
            raise ValueError("Contact has no id.")
        post_request(f"contacts/{self.id}", method="delete")
        # remove the id from the object
        self.id = None
        return self

    @staticmethod
    def find_by_id(contact_id: int) -> "Contact":
        data = post_request(f"contacts/{contact_id}", method="get")
        return Contact.from_dict(data)

    @staticmethod
    def find_by_customer_id(customer_id: str) -> "Contact":
        data = post_request(f"contacts/customer_id/{customer_id}", method="get")
        return Contact.from_dict(data)

    @staticmethod
    def delete_by_id(contact_id: int) -> "Contact":
        contact = Contact.find_by_id(contact_id)
        return contact.delete()

    def save(self) -> None:
        if self.id is None:
            data = post_request(
                "contacts", data={"contact": self.model_dump()}, method="post"
            )
            # update the current object with the data
            self.update(data)
        else:
            data = post_request(
                f"contacts/{self.id}",
                data={"contact": self.model_dump()},
                method="patch",
            )
            self.update(data)
