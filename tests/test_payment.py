from typing import Any
import pytest
from moneysnake.payment import Payment
from pytest_mock import MockType


@pytest.fixture(name="payment_data")
def fixture_payment_data() -> dict[str, str | int | None]:
    return {
        "id": "433546310070568441",
        "administration_id": 123,
        "invoice_type": "SalesInvoice",
        "invoice_id": "433546309874484716",
        "financial_account_id": "433546310057985525",
        "user_id": 1,
        "payment_transaction_id": None,
        "transaction_identifier": None,
        "price": "363.0",
        "price_base": "363.0",
        "payment_date": "2024-09-30",
        "credit_invoice_id": None,
        "financial_mutation_id": "433546310065325560",
        "ledger_account_id": "433546310050645492",
        "linked_payment_id": None,
        "manual_payment_action": None,
        "created_at": "2024-09-30T07:40:02.576Z",
        "updated_at": "2024-09-30T07:40:02.576Z",
    }


def test_payment(payment_data: dict[str, Any], mocker: MockType):
    payment = Payment(**payment_data)

    assert payment.payment_date == "2024-09-30"
    assert payment.price == 363.0
    assert isinstance(payment.price, float)

    with pytest.raises(NotImplementedError):
        payment.save()

    with pytest.raises(NotImplementedError):
        payment.delete()
