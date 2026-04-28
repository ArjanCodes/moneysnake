from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from .client import http_delete, http_get, http_get_raw, http_patch, http_post, paginate
from .custom_field_model import CustomFieldModel
from .model import Synchronizable, ensure_list_of
from .payment import Payment


class SalesInvoiceDetailsAttribute(BaseModel):
    """Details attribute (line item) for a sales invoice."""

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


class SalesInvoice(Synchronizable, CustomFieldModel):
    """Represents a sales invoice in Moneybird."""

    _endpoint: str | None = "sales_invoice"

    contact_id: int | None = None
    contact_person_id: int | None = None
    invoice_id: str | None = None
    draft_id: int | None = None
    workflow_id: int | None = None
    document_style_id: int | None = None
    identity_id: int | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    payment_conditions: str | None = None
    payment_reference: str | None = None
    short_payment_reference: str | None = None
    reference: str | None = None
    language: str | None = None
    currency: str | None = None
    discount: str | None = None
    first_due_interval: int | None = None
    prices_are_incl_tax: bool | None = None
    state: str | None = None
    paused: bool | None = None
    total_paid: str | None = None
    total_unpaid: str | None = None
    total_unpaid_base: str | None = None
    total_price_excl_tax: str | None = None
    total_price_excl_tax_base: str | None = None
    total_price_incl_tax: str | None = None
    total_price_incl_tax_base: str | None = None
    total_discount: str | None = None
    paid_at: str | None = None
    sent_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    version: int | None = None
    marked_dubious_on: str | None = None
    marked_uncollectible_on: str | None = None
    url: str | None = None
    payment_url: str | None = None
    public_view_code: str | None = None
    reminder_count: int | None = None
    next_reminder: str | None = None
    original_estimate_id: int | None = None
    recurring_sales_invoice_id: int | None = None
    subscription_id: int | None = None

    details: list[SalesInvoiceDetailsAttribute] = Field(default_factory=list)
    payments: list[Payment] = Field(default_factory=list)
    tax_totals: list[dict[str, Any]] = Field(default_factory=list)

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
        value: list[dict[str, Any]] | list[SalesInvoiceDetailsAttribute] | None,
    ) -> list[SalesInvoiceDetailsAttribute]:
        if value is None:
            return []
        return ensure_list_of(SalesInvoiceDetailsAttribute, value)

    def save(self) -> None:
        """Save the sales invoice."""
        invoice_data = self.to_dict()
        details = invoice_data.pop("details", [])
        for detail_id in self._destroyed_detail_ids:
            details.append({"id": detail_id, "_destroy": True})
        invoice_data["details_attributes"] = details
        if "custom_fields" in invoice_data:
            invoice_data["custom_fields_attributes"] = invoice_data.pop("custom_fields")

        if self.id is None:
            data = http_post(
                f"{self.endpoint}s",
                data={self.endpoint: invoice_data},
            )
        else:
            data = http_patch(
                f"{self.endpoint}s/{self.id}",
                data={self.endpoint: invoice_data},
            )
        self._destroyed_detail_ids.clear()
        self.update(data)

    # --- Detail management ---

    def add_detail(self, detail: SalesInvoiceDetailsAttribute) -> None:
        self.details.append(detail)

    def get_detail(self, detail_id: int) -> SalesInvoiceDetailsAttribute:
        for detail in self.details:
            if detail.id == detail_id:
                return detail
        raise ValueError(f"Detail with id {detail_id} not found.")

    def update_detail(
        self, detail_id: int, data: dict[str, Any]
    ) -> SalesInvoiceDetailsAttribute:
        detail = self.get_detail(detail_id)
        detail.update(data)
        return detail

    def delete_detail(self, detail_id: int) -> None:
        detail = self.get_detail(detail_id)
        if detail.id is not None:
            self._destroyed_detail_ids.append(detail.id)
        self.details = [d for d in self.details if d.id != detail_id]

    # --- Payment management ---

    def create_payment(self, payment: Payment) -> None:
        """Register a payment for this sales invoice."""
        data = http_post(
            path=f"{self.endpoint}s/{self.id}/payments",
            data={"payment": payment.to_dict()},
        )
        payment_data = data.get("payment")
        if payment_data:
            self.payments.append(Payment(**payment_data))

    def delete_payment(self, payment_id: int) -> None:
        """Delete a payment from this sales invoice."""
        http_delete(path=f"{self.endpoint}s/{self.id}/payments/{payment_id}")
        self.payments = [p for p in self.payments if p.id != payment_id]

    # --- Actions ---

    def send_invoice(
        self,
        delivery_method: str | None = None,
        sending_scheduled: bool = False,
        deliver_ubl: bool = False,
        mergeable: bool = False,
        email_address: str | None = None,
        email_message: str | None = None,
    ) -> None:
        """Send the sales invoice."""
        body: dict[str, Any] = {}
        if delivery_method is not None:
            body["delivery_method"] = delivery_method
        if sending_scheduled:
            body["sending_scheduled"] = sending_scheduled
        if deliver_ubl:
            body["deliver_ubl"] = deliver_ubl
        if mergeable:
            body["mergeable"] = mergeable
        if email_address is not None:
            body["email_address"] = email_address
        if email_message is not None:
            body["email_message"] = email_message

        data = http_post(
            f"{self.endpoint}s/{self.id}/send_invoice",
            data={"sales_invoice_sending": body} if body else None,
        )
        self.update(data)

    def download_pdf(self) -> bytes:
        """Download the invoice PDF. Returns raw PDF bytes."""
        response = http_get_raw(f"{self.endpoint}s/{self.id}/download_pdf")
        return response.content

    def download_ubl(self) -> bytes:
        """Download the invoice in UBL format. Returns raw bytes."""
        response = http_get_raw(f"{self.endpoint}s/{self.id}/download_ubl")
        return response.content

    def pause(self) -> None:
        """Pause workflow reminders for this invoice."""
        data = http_post(f"{self.endpoint}s/{self.id}/pause")
        self.update(data)

    def resume(self) -> None:
        """Resume workflow reminders for this invoice."""
        data = http_post(f"{self.endpoint}s/{self.id}/resume")
        self.update(data)

    def mark_as_dubious(self) -> None:
        """Mark the invoice as dubious."""
        data = http_post(f"{self.endpoint}s/{self.id}/mark_as_dubious")
        self.update(data)

    def mark_as_uncollectible(self) -> None:
        """Mark the invoice as uncollectible."""
        data = http_post(f"{self.endpoint}s/{self.id}/mark_as_uncollectible")
        self.update(data)

    def register_payment(self, payment: Payment) -> None:
        """Register a payment via the register_payment endpoint."""
        data = http_post(
            f"{self.endpoint}s/{self.id}/register_payment",
            data={"payment": payment.to_dict()},
        )
        self.update(data)

    def duplicate_creditinvoice(self) -> "SalesInvoice":
        """Create a credit invoice for this invoice."""
        data = http_post(f"{self.endpoint}s/{self.id}/duplicate_creditinvoice")
        return SalesInvoice(**data)

    # --- Lookup helpers ---

    @classmethod
    def list_all(
        cls,
        state: str | None = None,
        period: str | None = None,
        contact_id: int | None = None,
        reference: str | None = None,
    ) -> list[Self]:
        """List sales invoices with optional filters."""
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

        data = paginate("sales_invoices", params=params or None)
        return [cls(**item) for item in data]

    @classmethod
    def find_by_invoice_id(cls, invoice_id: str) -> Self:
        """Find a sales invoice by its invoice_id (e.g. '2026-0001')."""
        data = http_get(f"sales_invoices/find_by_invoice_id/{invoice_id}")
        return cls(**data)

    @classmethod
    def find_by_reference(cls, reference: str) -> Self:
        """Find a sales invoice by its reference."""
        data = http_get(f"sales_invoices/find_by_reference/{reference}")
        return cls(**data)
