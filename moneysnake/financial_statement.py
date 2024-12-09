from typing import Any, List, Optional, Self
from dataclasses import dataclass, field

from .model import MoneybirdModel
from .financial_mutation import FinancialMutation
from .client import post_request


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

    def save(self) -> None:
        """
        Save the external sales invoice. Overrides the save method in MoneybirdModel.
        """
        financial_statement_data = self.to_dict()

        # For the POST and PATCH requests we need to use the details_attributes key
        # instead of details key to match the Moneybird API.
        financial_statement_data["financial_mutations_attributes"] = (
            financial_statement_data.pop("financial_mutations", [])
        )

        if self.id is None:
            data = post_request(
                f"{self.endpoint}s",
                data={self.endpoint: financial_statement_data},
                method="post",
            )

        else:
            data = post_request(
                f"{self.endpoint}s/{self.id}",
                data={self.endpoint: financial_statement_data},
                method="patch",
            )
        self.update(data)

    def load(self, id: int) -> None:
        raise NotImplementedError(
            "Financial statements cannot be loaded from Moneybird."
        )

    def add_financial_mutation(self, financial_mutation: FinancialMutation) -> None:
        """
        Add a financial mutation to the financial statement.
        """
        if not isinstance(financial_mutation, FinancialMutation):
            # If the financial mutation is not an instance of FinancialMutation,
            # Try to create one from the financial mutation.
            try:
                financial_mutation = FinancialMutation.from_dict(financial_mutation)
            except Exception as e:
                raise ValueError(
                    f"Invalid financial mutation. {e}. Financial mutation must be an instance of FinancialMutation."
                ) from e
        self.financial_mutations.append(financial_mutation.to_dict(exclude_none=True))

    @classmethod
    def find_by_id(cls: type[Self], id: int) -> Self:
        raise NotImplementedError(
            "Financial statements cannot be loaded from Moneybird."
        )
