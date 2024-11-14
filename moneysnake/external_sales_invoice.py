from dataclasses import dataclass
from typing import Optional, List

from .model import MoneybirdModel


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


# External sales invoices don't have custom fields, so we use MoneybirdModel
# instead of CustomFieldModel.
class ExternalSalesInvoice(MoneybirdModel):
    """
    Represents an external sales invoice in Moneybird.
    """

    contact_id: int
    reference: Optional[str] = None
    date: str
    due_date: Optional[str] = None
    currency: str
    prices_are_incl_tax: bool
    source: str
    source_url: str
    details_attributes: List[ExternalSalesInvoiceDetailsAttributes]
