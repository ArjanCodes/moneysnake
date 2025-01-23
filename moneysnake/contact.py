from dataclasses import dataclass

from .client import post_request
from .custom_field_model import CustomFieldModel


@dataclass
class ContactPerson:
    firstname: str | None = None
    lastname: str | None = None


@dataclass
class Contact(CustomFieldModel):
    company_name: str | None = None
    address1: str | None = None
    address2: str | None = None
    zipcode: str | None = None
    city: str | None = None
    country: str | None = None
    phone: str | None = None
    delivery_method: str | None = None
    customer_id: str | None = None
    tax_number: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    chamber_of_commerce: str | None = None
    bank_account: str | None = None
    send_invoices_to_attention: str | None = None
    send_invoices_to_email: str | None = None
    send_estimates_to_attention: str | None = None
    send_estimates_to_email: str | None = None
    sepa_active: bool = False
    sepa_iban: str | None = None
    sepa_iban_account_name: str | None = None
    sepa_bic: str | None = None
    sepa_mandate_id: str | None = None
    sepa_mandate_date: str | None = None
    sepa_sequence_type: str | None = None
    si_identifier_type: str | None = None
    si_identifier: str | None = None
    invoice_workflow_id: int | None = None
    estimate_workflow_id: int | None = None
    email_ubl: bool = False
    direct_debit: bool = False
    contact_person: ContactPerson | None = None
    type: str | None = None
    from_checkout: bool = False

    @staticmethod
    def find_by_customer_id(customer_id: str) -> "Contact":
        """
        Find a contact by customer_id
        """
        data = post_request(f"contacts/customer_id/{customer_id}", method="get")
        return Contact.from_dict(data)
