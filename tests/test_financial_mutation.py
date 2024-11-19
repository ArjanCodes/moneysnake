import pytest
from moneysnake.financial_mutation import (
    FinancialMutation,
    LinkBookingType,
    UnlinkBookingType,
)
from pytest_mock import MockType


@pytest.fixture(name="mutation_data")
def fixture_mutation_data():
    """
    Return a dictionary with data for a financial mutation.
    """
    return {
        "id": "433546259519768528",
        "administration_id": "123",
        "amount": "100.0",
        "code": "FM123",
        "date": "2024-09-30",
        "message": "Test mutation",
        "contra_account_name": "Test Account",
        "contra_account_number": "NL00TEST0123456789",
        "state": "open",
        "amount_open": "100.0",
        "sepa_fields": None,
        "batch_reference": None,
        "financial_account_id": "433546158492616512",
        "currency": "EUR",
        "original_amount": "100.0",
        "created_at": "2024-09-30T07:39:14.368Z",
        "updated_at": "2024-09-30T07:39:14.368Z",
        "version": "1",
        "financial_statement_id": None,
        "processed_at": None,
        "account_servicer_transaction_id": None,
        "payments": [],
        "ledger_account_bookings": [],
    }


def test_book_payment(mocker: MockType, mutation_data):
    """
    Test booking a payment on a financial mutation.
    """
    mock_post_request = mocker.patch("moneysnake.financial_mutation.post_request")
    mutation = FinancialMutation.from_dict(mutation_data)
    mutation.book_payment(100.0, 123, LinkBookingType.LedgerAccount)
    mock_post_request.assert_called_once_with(
        f"financial_mutations/{mutation.id}/link_booking",
        {
            "price_base": 100.0,
            "booking_id": 123,
            "booking_type": LinkBookingType.LedgerAccount,
        },
        method="PATCH",
    )


def test_remove_payment(mocker: MockType, mutation_data):
    """
    Test removing a payment from a financial mutation.
    """
    mock_post_request = mocker.patch("moneysnake.financial_mutation.post_request")
    mutation = FinancialMutation.from_dict(mutation_data)
    mutation.remove_payment(123, UnlinkBookingType.LedgerAccountBooking)
    mock_post_request.assert_called_once_with(
        f"financial_mutations/{mutation.id}/unlink_booking",
        {"booking_id": 123, "booking_type": UnlinkBookingType.LedgerAccountBooking},
        method="PATCH",
    )
