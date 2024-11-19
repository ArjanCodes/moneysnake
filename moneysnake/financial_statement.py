from typing import List, Optional, Self
from dataclasses import dataclass, field

from .model import MoneybirdModel
from .financial_mutation import FinancialMutation


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

    def load(self, id: int) -> None:
        raise NotImplementedError(
            "Financial statements cannot be loaded from Moneybird."
        )

    @classmethod
    def find_by_id(cls: type[Self], id: int) -> Self:
        raise NotImplementedError(
            "Financial statements cannot be loaded from Moneybird."
        )
