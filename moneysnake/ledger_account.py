from typing import Self

from pydantic import BaseModel, ConfigDict, Field

from .client import http_get
from .model import Loadable, MoneybirdModel


class TaxonomyItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    taxonomy_version: str | None = None
    code: str | None = None
    name: str | None = None
    name_english: str | None = None
    reference: str | None = None


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
    taxonomy_item: TaxonomyItem | None = None
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
