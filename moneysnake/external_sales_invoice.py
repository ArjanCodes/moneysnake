from typing import Any, Self

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from .client import http_delete, http_patch, http_post, paginate
from .model import CrudModel, Synchronizable, ensure_list_of
from .payment import Payment


class ExternalSalesInvoiceDetailsAttribute(BaseModel):
    """
    Details attribute for an external sales invoice.
    """

    id: int | None = None
    description: str | None = None
    period: str | None = None
    price: int | str | None = None
    amount: int | str | None = None
    tax_rate_id: int | None = None
    ledger_account_id: str | None = None
    project_id: str | None = None

    def update(self, data: dict[str, Any]) -> None:
        validated = self.model_validate({**self.model_dump(), **data})
        for key in self.__class__.model_fields:
            object.__setattr__(self, key, getattr(validated, key))



class ExternalSalesInvoice(Synchronizable, CrudModel):
    """
    Represents an external sales invoice in Moneybird.
    """

    contact_id: int | None = None
    reference: str | None = None
    date: str | None = None
    due_date: str | None = None
    currency: str | None = None
    prices_are_incl_tax: bool | None = None
    source: str | None = None
    source_url: str | None = None
    details: list[ExternalSalesInvoiceDetailsAttribute] | None = Field(
        default_factory=list
    )
    payments: list[Payment] | None = Field(default_factory=list)

    _destroyed_detail_ids: list[int] = PrivateAttr(default_factory=list)

    @field_validator("payments")
    def ensure_payments(
        cls, value: list[dict[str, Any]] | list[Payment] | None
    ) -> list[Payment] | None:
        if value is None:
            return None
        return ensure_list_of(Payment, value)

    def save(self) -> None:
        """
        Save the external sales invoice. Overrides the save method in MoneybirdModel.
        """
        invoice_data = self.to_dict()
        # For the POST and PATCH requests we need to use the details_attributes key
        # instead of details key to match the Moneybird API.
        details = invoice_data.pop("details", [])
        for detail_id in self._destroyed_detail_ids:
            details.append({"id": detail_id, "_destroy": True})
        invoice_data["details_attributes"] = details

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

    def add_detail(self, detail: ExternalSalesInvoiceDetailsAttribute) -> None:
        """
        Add a detail to the external sales invoice.
        """
        if self.details is None:
            self.details = []

        self.details.append(detail)

    def get_detail(self, detail_id: int) -> ExternalSalesInvoiceDetailsAttribute:
        """
        Get a detail from the external sales invoice.
        """

        if not self.details:
            raise ValueError("No details found.")

        for detail in self.details:
            if detail.id == detail_id:
                return detail
        raise ValueError(f"Detail with id {detail_id} not found.")

    def update_detail(
        self, detail_id: int, data: dict[str, Any]
    ) -> ExternalSalesInvoiceDetailsAttribute:
        """
        Update a detail from the external sales invoice.
        """
        detail = self.get_detail(detail_id)
        detail.update(data)
        return detail

    def delete_detail(self, detail_id: int) -> None:
        """
        Delete a detail from the external sales invoice.
        """
        detail = self.get_detail(detail_id)
        if detail.id is not None:
            self._destroyed_detail_ids.append(detail.id)
        if self.details:
            self.details = [detail for detail in self.details if detail.id != detail_id]

    @classmethod
    def list_all_by_contact_id(
        cls,
        contact_id: int,
        state: str | None = "all",
        period: str | None = "this_year",
    ) -> list[Self]:
        """
        List all external sales invoices for a contact.
        """
        endpoint = cls._sync_endpoint()
        data = paginate(
            f"{endpoint}s",
            params={"filter": f"contact_id:{contact_id},state:{state},period:{period}"},
        )
        return [cls(**item) for item in data]

    def create_payment(self, payment: Payment) -> Payment:
        """
        Create a payment for the external sales invoice.
        """
        data = http_post(
            path=f"{self.endpoint}s/{self.id}/payments",
            data={"payment": payment.to_dict()},
        )
        # Moneybird returns the created payment's fields at the top level; some
        # responses wrap them under a "payment" key. Accept either, and fall
        # back to the payment we sent if the response carries no body.
        payload = data.get("payment", data) if isinstance(data, dict) else None
        created = Payment(**payload) if payload else payment

        if self.payments is None:
            self.payments = []

        self.payments.append(created)
        return created

    def delete_payment(self, payment_id: int) -> None:
        """
        Delete a payment for the external sales invoice.
        """
        http_delete(
            path=f"{self.endpoint}s/{self.id}/payments/{payment_id}",
        )

        if not self.payments:
            raise ValueError("No payments found.")

        self.payments = [
            payment for payment in self.payments if payment.id != payment_id
        ]
