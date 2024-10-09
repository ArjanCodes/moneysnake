from dataclasses import dataclass
from typing import Optional

from .client import post_request
from .custom_field_model import CustomFieldModel


@dataclass
class ContactPerson:
    firstname: Optional[str] = None
    lastname: Optional[str] = None


@dataclass
class Contact(CustomFieldModel):
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
    type: Optional[str] = None
    from_checkout: bool = False

    @staticmethod
    def find_by_customer_id(customer_id: str) -> "Contact":
        data = post_request(f"contacts/customer_id/{customer_id}", method="get")
        return Contact.from_dict(data)
