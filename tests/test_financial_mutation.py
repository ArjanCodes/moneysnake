from typing import Any

import pytest
from pytest_mock import MockType

from moneysnake.financial_mutation import (
    FinancialMutation,
    FinancialMutationPayment,
    LedgerAccountBooking,
    LinkBookingType,
    UnlinkBookingType,
)


@pytest.fixture(name="mutation_data")
def fixture_mutation_data() -> dict[str, Any]:
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
        "state": "unprocessed",
        "settlement_state": "open",
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


def test_book_payment(mocker: MockType, mutation_data: dict[str, Any]):
    """
    Test booking a payment on a financial mutation.
    """
    mock_make_request = mocker.patch("moneysnake.financial_mutation.http_patch")
    mutation = FinancialMutation(**mutation_data)
    mutation.book_payment(100.0, 123, LinkBookingType.LedgerAccount)
    mock_make_request.assert_called_once_with(
        f"financial_mutations/{mutation.id}/link_booking",
        {
            "price_base": 100.0,
            "booking_id": 123,
            "booking_type": LinkBookingType.LedgerAccount.name,
        },
    )


def test_remove_payment(mocker: MockType, mutation_data: dict[str, Any]):
    """
    Test removing a payment from a financial mutation.
    """
    mock_make_request = mocker.patch("moneysnake.financial_mutation.http_delete")
    mutation = FinancialMutation(**mutation_data)
    mutation.remove_payment(123, UnlinkBookingType.LedgerAccountBooking)
    mock_make_request.assert_called_once_with(
        f"financial_mutations/{mutation.id}/unlink_booking",
        {
            "booking_id": 123,
            "booking_type": UnlinkBookingType.LedgerAccountBooking.name,
        },
    )


def test_load_typed_payments_and_bookings(
    mutation_data: dict[str, Any], payment_data: dict[str, Any]
):
    """
    Test that payments and ledger account bookings load as typed models.
    """
    mutation_data["payments"] = [payment_data]
    mutation_data["ledger_account_bookings"] = [
        {
            "id": "433546310080005632",
            "administration_id": "123",
            "financial_mutation_id": "433546259519768528",
            "ledger_account_id": "433546310050645492",
            "project_id": None,
            "description": "Office supplies",
            "price": "100.0",
            "created_at": "2024-09-30T07:40:02.576Z",
            "updated_at": "2024-09-30T07:40:02.576Z",
        }
    ]
    mutation = FinancialMutation(**mutation_data)

    payment = mutation.payments[0]
    assert isinstance(payment, FinancialMutationPayment)
    assert payment.id == 433546310070568441
    assert payment.invoice_type == "SalesInvoice"
    assert payment.user_id == 1727681857838
    assert payment.price == 363.0
    assert payment.financial_mutation_id == 433546310065325560
    assert payment.manual_payment_action == "bank_transfer"
    assert payment.linked_payment_id is None

    booking = mutation.ledger_account_bookings[0]
    assert isinstance(booking, LedgerAccountBooking)
    assert booking.id == 433546310080005632
    assert booking.ledger_account_id == 433546310050645492
    assert booking.description == "Office supplies"
    assert booking.price == 100.0
    assert booking.project_id is None


def test_payment_read_model_has_no_manual_payment_action_default():
    """
    Test that the read model does not invent a manual payment action.
    """
    assert FinancialMutationPayment().manual_payment_action is None
