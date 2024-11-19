from model import MoneybirdModel

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FinancialMutation:
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


@dataclass
class FinancialStatement(MoneybirdModel):
    """
    Represents a financial statement in Moneybird.
    """

    financial_account_id: Optional[str] = None
    reference: Optional[str] = None
    official_date: Optional[str] = None
    official_balance: Optional[str] = None
    importer_service: Optional[str] = None
    financial_mutations: List[FinancialMutation] = field(default_factory=list)
