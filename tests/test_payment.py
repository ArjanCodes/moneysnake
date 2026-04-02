from typing import Any

from moneysnake.payment import Payment


def test_payment(payment_data: dict[str, Any]):
    payment = Payment(**payment_data)

    assert payment.payment_date == "2024-09-30"
    assert payment.price == 363.0
    assert isinstance(payment.price, float)


def test_payment_has_no_save_or_delete(payment_data: dict[str, Any]):
    """Payment should not have save() or delete() methods."""
    payment = Payment(**payment_data)
    assert not hasattr(payment, "save")
    assert not hasattr(payment, "delete")
