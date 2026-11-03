from typing import Any, Self

from pydantic import Field

from .client import http_get
from .model import Loadable, MoneybirdModel


class LedgerAccount(Loadable, MoneybirdModel):
    """
    Represents a Ledger Account in Moneybird.
    """

    administration_id: int | None = None
    name: str | None = None
    account_type: str | None = None
    account_id: str | None = None
    parent_id: int | None = None
    active: bool | None = None
    allowed_document_types: list[str] = Field(default_factory=list)
    taxonomy_item: dict[str, Any] | None = None
    financial_account_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def list_all(cls) -> list[Self]:
        """
        List all ledger accounts for the administration.
        """
        data = http_get("ledger_accounts")
        return [cls(**account) for account in data]
