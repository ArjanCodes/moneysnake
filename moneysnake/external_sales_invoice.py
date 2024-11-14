from dataclasses import dataclass
from typing import Any, Optional, List, Self

from .model import MoneybirdModel
from .client import post_request


@dataclass
class ExternalSalesInvoiceDetailsAttributes:
    """
    Details attributes for an external sales invoice.
    """

    id: int
    description: str
    period: str
    price: int
    amount: int
    tax_rate_id: int
    ledger_account_id: str
    project_id: str


@dataclass
class ExternalSalesInvoicePayment:
    """
    Represents a payment on an external sales invoice.
    """

    payment_date: str
    price: float
    price_base: float
    financial_account_id: int
    financial_mutation_id: int
    manual_payment_action: str = "bank_transfer"
    transaction_identifier: Optional[str] = None
    ledger_account_id: Optional[int] = None
    invoice_id: Optional[int] = None


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
    details: Optional[List[ExternalSalesInvoiceDetailsAttributes]] = None
    payments: Optional[List[ExternalSalesInvoicePayment]] = None

    def save(self) -> None:
        """
        Save the external sales invoice. Overrides the save method in MoneybirdModel.
        """
        invoice_data = self.to_dict()
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

    def update(self, data: dict[str, Any]) -> None:
        """
        Update the external sales invoice with the given data.
        """
        for key, value in data.items():
            if key == "details":
                key = "details_attributes"
            if hasattr(self, key):
                setattr(self, key, value)

    def create_payment(
        self, payment: ExternalSalesInvoicePayment
    ) -> ExternalSalesInvoicePayment:
        """
        Create a payment for the external sales invoice.
        """
        data = post_request(
            path=f"{self.endpoint}s/{self.id}/payments",
            data={"payment": payment.__dict__},
        )

        return ExternalSalesInvoicePayment(**data["payment"])
