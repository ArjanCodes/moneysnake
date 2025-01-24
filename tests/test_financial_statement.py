from typing import Any
import pytest
from pytest_mock import MockType
from moneysnake.financial_statement import FinancialStatement


@pytest.fixture(name="statement_data")
def fixture_statement_data() -> dict[str, Any]:
    """
    Return a dictionary with data for a financial statement.
    """
    return {
        "id": "433546265561662832",
        "financial_account_id": "433546265495602541",
        "reference": "31012014_ABNAMRO",
        "official_date": None,
        "official_balance": None,
        "importer_service": None,
        "financial_mutations": [
            {
                "id": "433546265562711409",
                "administration_id": 123,
                "amount": "100.0",
                "code": None,
                "date": "2024-09-30",
                "message": "Foobar 1",
                "contra_account_name": None,
                "contra_account_number": "",
                "state": "unprocessed",
                "amount_open": "100.0",
                "sepa_fields": None,
                "batch_reference": None,
                "financial_account_id": "433546265495602541",
                "currency": "EUR",
                "original_amount": None,
                "created_at": "2024-09-30T07:39:20.132Z",
                "updated_at": "2024-09-30T07:39:20.132Z",
                "version": 1727681960,
                "financial_statement_id": "433546265561662832",
                "processed_at": None,
                "account_servicer_transaction_id": None,
                "payments": [],
                "ledger_account_bookings": [],
            },
            {
                "id": "433546265564808562",
                "administration_id": 123,
                "amount": "200.0",
                "code": None,
                "date": "2024-09-30",
                "message": "Foobar 2",
                "contra_account_name": None,
                "contra_account_number": "",
                "state": "unprocessed",
                "amount_open": "200.0",
                "sepa_fields": None,
                "batch_reference": None,
                "financial_account_id": "433546265495602541",
                "currency": "EUR",
                "original_amount": None,
                "created_at": "2024-09-30T07:39:20.133Z",
                "updated_at": "2024-09-30T07:39:20.133Z",
                "version": 1727681960,
                "financial_statement_id": "433546265561662832",
                "processed_at": None,
                "account_servicer_transaction_id": None,
                "payments": [],
                "ledger_account_bookings": [],
            },
        ],
    }


def test_create_financial_statement(mocker: MockType, statement_data: dict[str, Any]):
    """
    Test creating a financial statement.
    """
    del statement_data["id"]
    mock_make_request = mocker.patch("moneysnake.financial_statement.http_post")
    mock_make_request.return_value = {"id": 433546265561662833, **statement_data}
    statement = FinancialStatement(**statement_data)
    statement.save()

    assert statement.id == 433546265561662833
    assert statement.reference == "31012014_ABNAMRO"
    assert len(statement.financial_mutations) == 2
