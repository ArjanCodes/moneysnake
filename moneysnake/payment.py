from dataclasses import dataclass
from typing import Optional

from .model import MoneybirdModel


@dataclass
class Payment(MoneybirdModel):
    """
    Represents a payment in Moneybird.
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

    def save(self) -> None:
        raise NotImplementedError(
            "Payments cannot be saved directly. Refer to the invoice that the payment is for."
        )

    def delete(self) -> None:
        raise NotImplementedError(
            "Payments cannot be deleted directly. Refer to the invoice that the payment is for."
        )
