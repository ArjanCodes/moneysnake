from typing import Self

from .client import http_get
from .model import MoneybirdModel


class TaxRate(MoneybirdModel):
    """
    Represents a Tax Rate in Moneybird.
    """

    name: str | None = None
    percentage: float | None = None
    tax_rate_type: str | None = None
    country: str | None = None
    active: bool | None = None
    administration_id: int | None = None
    show_tax: bool | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def list_all_rates(cls) -> list[Self]:
        """
        List all available tax rates for the administration.
        """
        data = http_get("tax_rates")
        return [cls(**rate) for rate in data]

    @classmethod
    def list_sales_rates(cls) -> list[Self]:
        """
        List all sales tax rates.
        """
        data = http_get("tax_rates?filter=tax_rate_type:sales_invoice")
        return [cls(**rate) for rate in data]

    @classmethod
    def find_sales_rate_by_country(cls, country: str) -> list[Self]:
        """
        Find sales tax rates by country.
        """
        data = http_get(
            f"tax_rates?filter=country:{country},tax_rate_type:sales_invoice"
        )
        return [cls(**rate) for rate in data]
