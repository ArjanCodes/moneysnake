from dataclasses import dataclass, field
import inspect
from typing import Any, Optional, List, Self

from .model import MoneybirdModel
from .client import post_request


@dataclass
class ExternalSalesInvoiceDetailsAttributes:
    """
    Details attributes for an external sales invoice.
    """

    id: Optional[int] = None
    description: Optional[str] = None
    period: Optional[str] = None
    price: Optional[int] = None
    amount: Optional[int] = None
    tax_rate_id: Optional[int] = None
    ledger_account_id: Optional[str] = None
    project_id: Optional[str] = None

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        return cls(
            **{k: v for k, v in data.items() if k in inspect.signature(cls).parameters}
        )


@dataclass
class ExternalSalesInvoicePayment:
    """
    Represents a payment on an external sales invoice.
    """

    payment_date: Optional[str] = None
    price: Optional[float] = None
    price_base: Optional[float] = None
    financial_account_id: Optional[int] = None
    financial_mutation_id: Optional[int] = None
    manual_payment_action: Optional[str] = "bank_transfer"
    transaction_identifier: Optional[str] = None
    ledger_account_id: Optional[int] = None
    invoice_id: Optional[int] = None

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        return cls(
            **{k: v for k, v in data.items() if k in inspect.signature(cls).parameters}
        )


# External sales invoices don't have custom fields, so we use MoneybirdModel
# instead of CustomFieldModel.
@dataclass
class ExternalSalesInvoice(MoneybirdModel):
    """
    Represents an external sales invoice in Moneybird.
    """

    contact_id: Optional[int] = None
    reference: Optional[str] = None
    date: Optional[str] = None
    due_date: Optional[str] = None
    currency: Optional[str] = None
    prices_are_incl_tax: Optional[bool] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    details: Optional[List[ExternalSalesInvoiceDetailsAttributes]] = field(
        default_factory=list
    )
    payments: Optional[List[ExternalSalesInvoicePayment]] = field(default_factory=list)

    def update(self, data: dict[str, Any]) -> None:
        super().update(data)
        # Construct the details and payments list of subclasses from the data.
        if isinstance(self.details, list):
            self.details = [
                ExternalSalesInvoiceDetailsAttributes.from_dict(detail)
                if isinstance(detail, dict)
                else detail
                for detail in self.details
            ]
        if isinstance(self.payments, list):
            self.payments = [
                ExternalSalesInvoicePayment.from_dict(payment)
                if isinstance(payment, dict)
                else payment
                for payment in self.payments
            ]

    def save(self) -> None:
        """
        Save the external sales invoice. Overrides the save method in MoneybirdModel.
        """
        invoice_data = self.to_dict()
        # For the POST and PATCH requests we need to use the details_attributes key
        # instead of details key to match the Moneybird API.
        invoice_data["details_attributes"] = invoice_data.pop("details", [])

        if self.id is None:
            data = post_request(
                f"{self.endpoint}s",
                data={self.endpoint: invoice_data},
                method="post",
            )
            self.update(data)
        else:
            data = post_request(
                f"{self.endpoint}s/{self.id}",
                data={self.endpoint: invoice_data},
                method="patch",
            )
            self.update(data)

    def list_all_by_contact_id(
        self,
        contact_id: int,
        state: Optional[str] = "all",
        period: Optional[str] = "this_year",
    ) -> List:
        """
        List all external sales invoices for a contact.
        """
        data = post_request(
            path=f"{self.endpoint}s/?filter=contact_id:{contact_id}&state:{state}&period:{period}",
            method="get",
        )

        invoices = []
        for invoice in data:
            invoice_obj = ExternalSalesInvoice.from_dict(invoice)
            if "details" in invoice:
                invoice_obj.details = [
                    ExternalSalesInvoiceDetailsAttributes.from_dict(detail)
                    for detail in invoice["details"]
                ]
            if "payments" in invoice:
                invoice_obj.payments = [
                    ExternalSalesInvoicePayment.from_dict(payment)
                    for payment in invoice["payments"]
                ]
            invoices.append(invoice_obj)
        return invoices

    def create_payment(
        self, payment: ExternalSalesInvoicePayment
    ) -> ExternalSalesInvoicePayment:
        """
        Create a payment for the external sales invoice.
        """
        data = post_request(
            path=f"{self.endpoint}s/{self.id}/payments",
            data={"payment": payment},
        )

        return ExternalSalesInvoicePayment.from_dict(data["payment"])
