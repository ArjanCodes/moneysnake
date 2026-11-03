from typing import Any

from pydantic import Field, field_validator

from moneysnake.client import http_patch, http_post

from .financial_mutation import FinancialMutation
from .model import Deletable, MoneybirdModel, Saveable, ensure_list_of


class FinancialStatement(Saveable, Deletable, MoneybirdModel):
    """
    Represents a financial statement in Moneybird.
    """

    financial_account_id: str | None = None
    reference: str | None = None
    official_date: str | None = None
    official_balance: str | None = None
    importer_service: str | None = None
    financial_mutations: list[FinancialMutation] = Field(default_factory=list)

    @field_validator("financial_mutations")
    def ensure_financial_mutations(
        cls, value: list[dict[str, Any]] | None
    ) -> list[FinancialMutation] | None:
        if value is None:
            return None
        return ensure_list_of(FinancialMutation, value)

    def _write_data(self) -> dict[str, Any]:
        data = super()._write_data()
        data.pop("financial_mutations", None)
        data["financial_mutations_attributes"] = [
            mutation.model_dump(exclude_unset=True)
            for mutation in self.financial_mutations
        ]
        return data

    def save(self) -> None:
        """
        Save the financial statement. Overrides the save method in MoneybirdModel.
        """
        financial_statement_data = self._write_data()

        if self.id is None:
            data = http_post(
                f"{self.endpoint}s",
                data={self.endpoint: financial_statement_data},
            )

        else:
            data = http_patch(
                f"{self.endpoint}s/{self.id}",
                data={self.endpoint: financial_statement_data},
            )
        self.update(data)

    def add_financial_mutation(self, financial_mutation: FinancialMutation) -> None:
        """
        Add a financial mutation to the financial statement.
        """
        self.financial_mutations.append(financial_mutation)
