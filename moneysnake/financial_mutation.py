from typing import Any, List, Optional, Self
from dataclasses import dataclass, field
from enum import Enum, auto

from .model import MoneybirdModel
from .client import post_request


class LinkBookingType(Enum):
    """
    Enum for the different types of bookings that can be linked to a financial mutation.
    """

    LedgerAccount = auto()
    SalesInvoice = auto()
    Document = auto()
    PaymentTransactionBatch = auto()
    PurchaseTransaction = auto()
    NewPurchaseInvoice = auto()
    NewReceipt = auto()
    PaymentTransaction = auto()
    PurchaseTransactionBatch = auto()
    ExternalSalesInvoice = auto()
    Payment = auto()
    VatDocument = auto()


class UnlinkBookingType(Enum):
    """
    Enum for the different types of bookings that can be unlinked from a financial mutation.
    """

    LedgerAccountBooking = auto()
    Payment = auto()


@dataclass
class FinancialMutation(MoneybirdModel):
    """
    Represents a financial mutation in Moneybird.
    """

    id: Optional[str] = None
    administration_id: Optional[str] = None
    amount: Optional[str] = None
    code: Optional[str] = None
    date: Optional[str] = None
    message: Optional[str] = None
    contra_account_name: Optional[str] = None
    contra_account_number: Optional[str] = None
    state: Optional[str] = None
    amount_open: Optional[str] = None
    sepa_fields: Optional[str] = None
    batch_reference: Optional[str] = None
    financial_account_id: Optional[str] = None
    currency: Optional[str] = None
    original_amount: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None
    financial_statement_id: Optional[str] = None
    processed_at: Optional[str] = None
    account_servicer_transaction_id: Optional[str] = None
    payments: List = field(default_factory=list)
    ledger_account_bookings: List = field(default_factory=list)

    # Disable create, update and delete methods for financial mutations as they don't
    # exist in the Moneybird API.
    def save(self) -> None:
        raise NotImplementedError("Financial mutations cannot be saved in Moneybird.")

    def delete(self) -> None:
        raise NotImplementedError("Financial mutations cannot be deleted in Moneybird.")

    def book_payment(
        self,
        price_base: float,
        booking_id: int,
        booking_type: LinkBookingType = LinkBookingType.LedgerAccount,
    ) -> None:
        """
        Book a payment on this financial mutation.
        """
        post_request(
            f"financial_mutations/{self.id}/link_booking",
            {
                "price_base": price_base,
                "booking_id": booking_id,
                "booking_type": booking_type,
            },
            method="PATCH",
        )

    def remove_payment(
        self,
        booking_id: int,
        booking_type: UnlinkBookingType = UnlinkBookingType.LedgerAccountBooking,
    ) -> None:
        """
        Remove a payment from this financial mutation.
        """
        post_request(
            f"financial_mutations/{self.id}/unlink_booking",
            {"booking_id": booking_id, "booking_type": booking_type},
            method="PATCH",
        )

    @classmethod
    def update_by_id(cls: type[Self], id: int, data: dict[str, Any]) -> Self:
        raise NotImplementedError("Financial mutations cannot be updated in Moneybird.")

    @classmethod
    def delete_by_id(cls: type[Self], id: int) -> Self:
        raise NotImplementedError("Financial mutations cannot be deleted in Moneybird.")
