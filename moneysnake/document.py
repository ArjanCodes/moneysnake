from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from .client import http_delete, http_get, http_patch, http_post, paginate
from .model import Synchronizable, ensure_list_of
from .payment import Payment


class DocumentDetailsAttribute(BaseModel):
    """Details attribute (line item) for a purchase invoice or receipt."""

    id: int | None = None
    description: str | None = None
    period: str | None = None
    price: int | str | None = None
    amount: int | str | None = None
    tax_rate_id: int | None = None
    ledger_account_id: int | str | None = None
    project_id: int | str | None = None
    product_id: int | str | None = None
    row_order: int | None = None
    model_config = ConfigDict(extra="ignore")

    def update(self, data: dict[str, Any]) -> None:
        validated = self.model_validate({**self.model_dump(), **data})
        for key in self.__class__.model_fields:
            object.__setattr__(self, key, getattr(validated, key))


class Document(Synchronizable):
    """Base class for Moneybird document types (purchase invoices, receipts).

    Subclasses must set ``_resource`` (e.g. ``"purchase_invoice"``). All requests
    are routed under ``documents/{_resource}s``.
    """

    _resource: ClassVar[str]

    contact_id: int | None = None
    contact: dict[str, Any] | None = None
    reference: str | None = None
    date: str | None = None
    due_date: str | None = None
    entry_number: int | None = None
    state: str | None = None
    currency: str | None = None
    exchange_rate: str | None = None
    revenue_invoice: bool | None = None
    prices_are_incl_tax: bool | None = None
    origin: str | None = None
    paid_at: str | None = None
    tax_number: str | None = None
    total_price_excl_tax: str | None = None
    total_price_excl_tax_base: str | None = None
    total_price_incl_tax: str | None = None
    total_price_incl_tax_base: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    version: int | None = None

    details: list[DocumentDetailsAttribute] = Field(default_factory=list)
    payments: list[Payment] = Field(default_factory=list)

    _destroyed_detail_ids: list[int] = PrivateAttr(default_factory=list)

    @field_validator("payments")
    def ensure_payments(
        cls, value: list[dict[str, Any]] | list[Payment] | None
    ) -> list[Payment]:
        if value is None:
            return []
        return ensure_list_of(Payment, value)

    @field_validator("details")
    def ensure_details(
        cls,
        value: list[dict[str, Any]] | list[DocumentDetailsAttribute] | None,
    ) -> list[DocumentDetailsAttribute]:
        if value is None:
            return []
        return ensure_list_of(DocumentDetailsAttribute, value)

    @classmethod
    def _base_path(cls) -> str:
        return f"documents/{cls._resource}s"

    @classmethod
    def _sync_endpoint(cls) -> str:
        return f"documents/{cls._resource}"

    def load(self, id: int) -> None:
        data = http_get(f"{self._base_path()}/{id}")
        self.update(data)

    @classmethod
    def find_by_id(cls: type[Self], id: int) -> Self:
        entity = cls(id=id)
        entity.load(id)
        return entity

    def save(self) -> None:
        body = self.to_dict()
        details = body.pop("details", [])
        for detail_id in self._destroyed_detail_ids:
            details.append({"id": detail_id, "_destroy": True})
        body["details_attributes"] = details

        if self.id is None:
            data = http_post(self._base_path(), data={self._resource: body})
        else:
            data = http_patch(
                f"{self._base_path()}/{self.id}", data={self._resource: body}
            )
        self._destroyed_detail_ids.clear()
        self.update(data)

    def delete(self) -> None:
        if not self.id:
            raise ValueError(f"Cannot delete {self.__class__.__name__} without an id")
        http_delete(f"{self._base_path()}/{self.id}")
        self.id = None

    def add_detail(self, detail: DocumentDetailsAttribute) -> None:
        self.details.append(detail)

    def get_detail(self, detail_id: int) -> DocumentDetailsAttribute:
        for detail in self.details:
            if detail.id == detail_id:
                return detail
        raise ValueError(f"Detail with id {detail_id} not found.")

    def update_detail(
        self, detail_id: int, data: dict[str, Any]
    ) -> DocumentDetailsAttribute:
        detail = self.get_detail(detail_id)
        detail.update(data)
        return detail

    def delete_detail(self, detail_id: int) -> None:
        detail = self.get_detail(detail_id)
        if detail.id is not None:
            self._destroyed_detail_ids.append(detail.id)
        self.details = [d for d in self.details if d.id != detail_id]

    def create_payment(self, payment: Payment) -> None:
        data = http_post(
            path=f"{self._base_path()}/{self.id}/payments",
            data={"payment": payment.to_dict()},
        )
        payment_data = data.get("payment")
        if payment_data:
            self.payments.append(Payment(**payment_data))

    def delete_payment(self, payment_id: int) -> None:
        http_delete(path=f"{self._base_path()}/{self.id}/payments/{payment_id}")
        self.payments = [p for p in self.payments if p.id != payment_id]

    def register_payment(self, payment: Payment) -> None:
        """Register a payment via the register_payment endpoint."""
        data = http_patch(
            f"{self._base_path()}/{self.id}/register_payment",
            data={"payment": payment.to_dict()},
        )
        self.update(data)

    @classmethod
    def list_all(
        cls,
        state: str | None = None,
        period: str | None = None,
        contact_id: int | None = None,
        reference: str | None = None,
    ) -> list[Self]:
        """List documents with optional filters."""
        filter_parts: list[str] = []
        if state:
            filter_parts.append(f"state:{state}")
        if period:
            filter_parts.append(f"period:{period}")
        if contact_id:
            filter_parts.append(f"contact_id:{contact_id}")
        if reference:
            filter_parts.append(f"reference:{reference}")

        params: dict[str, str] = {}
        if filter_parts:
            params["filter"] = ",".join(filter_parts)

        data = paginate(cls._base_path(), params=params or None)
        return [cls(**item) for item in data]
