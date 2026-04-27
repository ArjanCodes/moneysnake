from typing import Any

import pytest
from pytest_mock import MockType

from moneysnake.payment import Payment
from moneysnake.document import DocumentDetailsAttribute
from moneysnake.purchase_invoice import (
    PurchaseInvoice,
    PurchaseInvoiceDetailsAttribute,
)


def test_save_new_purchase_invoice(mocker: MockType, document_data: dict[str, Any]):
    del document_data["id"]
    mock_post = mocker.patch("moneysnake.document.http_post")
    mock_post.return_value = {"id": 480487019028416410, **document_data}
    invoice = PurchaseInvoice(**document_data)
    invoice.save()
    assert invoice.id == 480487019028416410
    mock_post.assert_called_once()
    assert mock_post.call_args[0][0] == "documents/purchase_invoices"
    call_data = mock_post.call_args[1]["data"]["purchase_invoice"]
    assert "details_attributes" in call_data
    assert "details" not in call_data


def test_update_existing_purchase_invoice(
    mocker: MockType, document_data: dict[str, Any]
):
    mock_patch = mocker.patch("moneysnake.document.http_patch")
    mock_patch.return_value = document_data
    invoice = PurchaseInvoice(**document_data)
    invoice.save()
    assert invoice.id == 480487019028416410
    assert (
        mock_patch.call_args[0][0]
        == "documents/purchase_invoices/480487019028416410"
    )


def test_find_by_id(mocker: MockType, document_data: dict[str, Any]):
    mock_get = mocker.patch("moneysnake.document.http_get", return_value=document_data)
    invoice = PurchaseInvoice.find_by_id(480487019028416410)
    assert invoice.reference == "2026-01234"
    assert invoice.state == "open"
    mock_get.assert_called_once_with(
        "documents/purchase_invoices/480487019028416410"
    )


def test_delete(mocker: MockType, document_data: dict[str, Any]):
    mock_delete = mocker.patch("moneysnake.document.http_delete")
    invoice = PurchaseInvoice(**document_data)
    invoice.delete()
    assert invoice.id is None
    mock_delete.assert_called_once_with(
        "documents/purchase_invoices/480487019028416410"
    )


def test_delete_without_id_raises(document_data: dict[str, Any]):
    document_data["id"] = None
    invoice = PurchaseInvoice(**document_data)
    with pytest.raises(ValueError, match="without an id"):
        invoice.delete()




def test_add_detail(document_data: dict[str, Any]):
    invoice = PurchaseInvoice(**document_data)
    detail = PurchaseInvoiceDetailsAttribute(
        description="New item", price="50.0", amount="2"
    )
    invoice.add_detail(detail)
    assert len(invoice.details) == 2


def test_get_detail(document_data: dict[str, Any]):
    invoice = PurchaseInvoice(**document_data)
    detail = invoice.get_detail(480487019122788274)
    assert detail.description == "Office supplies"


def test_get_detail_not_found(document_data: dict[str, Any]):
    invoice = PurchaseInvoice(**document_data)
    with pytest.raises(ValueError, match="not found"):
        invoice.get_detail(999)


def test_update_detail(document_data: dict[str, Any]):
    invoice = PurchaseInvoice(**document_data)
    detail = invoice.update_detail(480487019122788274, {"description": "Updated"})
    assert detail.description == "Updated"


def test_delete_detail(document_data: dict[str, Any]):
    invoice = PurchaseInvoice(**document_data)
    invoice.delete_detail(480487019122788274)
    assert len(invoice.details) == 0




def test_create_payment(
    mocker: MockType, document_data: dict[str, Any], payment_data: dict[str, Any]
):
    mock_post = mocker.patch("moneysnake.document.http_post")
    mock_post.return_value = {"payment": payment_data}
    invoice = PurchaseInvoice(**document_data)
    invoice.create_payment(Payment(**payment_data))
    assert len(invoice.payments) == 1
    assert invoice.payments[0].id == 433546310070568441
    assert (
        mock_post.call_args[1]["path"]
        == "documents/purchase_invoices/480487019028416410/payments"
    )


def test_delete_payment(
    mocker: MockType, document_data: dict[str, Any], payment_data: dict[str, Any]
):
    mock_post = mocker.patch("moneysnake.document.http_post")
    mock_post.return_value = {"payment": payment_data}
    invoice = PurchaseInvoice(**document_data)
    invoice.create_payment(Payment(**payment_data))

    mock_delete = mocker.patch("moneysnake.document.http_delete")
    invoice.delete_payment(433546310070568441)
    assert len(invoice.payments) == 0
    mock_delete.assert_called_once_with(
        path="documents/purchase_invoices/480487019028416410/payments/433546310070568441"
    )


def test_register_payment(
    mocker: MockType, document_data: dict[str, Any], payment_data: dict[str, Any]
):
    mock_post = mocker.patch("moneysnake.document.http_post")
    mock_post.return_value = {**document_data, "state": "paid", "paid_at": "2026-04-27"}
    invoice = PurchaseInvoice(**document_data)
    invoice.register_payment(Payment(**payment_data))
    assert invoice.state == "paid"
    assert (
        mock_post.call_args[0][0]
        == "documents/purchase_invoices/480487019028416410/register_payment"
    )




def test_list_all(mocker: MockType, document_data: dict[str, Any]):
    mock_paginate = mocker.patch("moneysnake.document.paginate")
    mock_paginate.return_value = [document_data, document_data]
    invoices = PurchaseInvoice.list_all(state="open", period="this_year")
    assert len(invoices) == 2
    assert mock_paginate.call_args[0][0] == "documents/purchase_invoices"
    call_params = mock_paginate.call_args[1]["params"]
    assert "state:open" in call_params["filter"]
    assert "period:this_year" in call_params["filter"]


def test_list_all_no_filters(mocker: MockType, document_data: dict[str, Any]):
    mock_paginate = mocker.patch("moneysnake.document.paginate")
    mock_paginate.return_value = [document_data]
    invoices = PurchaseInvoice.list_all()
    assert len(invoices) == 1
    mock_paginate.assert_called_once_with("documents/purchase_invoices", params=None)




def test_payments_converted_from_dicts(
    mocker: MockType, document_data: dict[str, Any], payment_data: dict[str, Any]
):
    document_data["payments"] = [payment_data]
    mocker.patch("moneysnake.document.http_get", return_value=document_data)
    invoice = PurchaseInvoice.find_by_id(480487019028416410)
    assert len(invoice.payments) == 1
    assert isinstance(invoice.payments[0], Payment)


def test_details_converted_from_dicts(document_data: dict[str, Any]):
    invoice = PurchaseInvoice(**document_data)
    assert len(invoice.details) == 1
    assert isinstance(invoice.details[0], DocumentDetailsAttribute)




def test_sync_endpoint():
    assert PurchaseInvoice._sync_endpoint() == "documents/purchase_invoice"
