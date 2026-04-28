from typing import Any

from pytest_mock import MockType

from moneysnake.receipt import Receipt, ReceiptDetailsAttribute


def test_save_new_receipt(mocker: MockType, document_data: dict[str, Any]):
    del document_data["id"]
    mock_post = mocker.patch("moneysnake.document.http_post")
    mock_post.return_value = {"id": 480487019028416410, **document_data}
    receipt = Receipt(**document_data)
    receipt.save()
    assert receipt.id == 480487019028416410
    assert mock_post.call_args[0][0] == "documents/receipts"
    call_data = mock_post.call_args[1]["data"]["receipt"]
    assert "details_attributes" in call_data


def test_find_by_id(mocker: MockType, document_data: dict[str, Any]):
    mock_get = mocker.patch("moneysnake.document.http_get", return_value=document_data)
    receipt = Receipt.find_by_id(480487019028416410)
    assert receipt.reference == "2026-01234"
    mock_get.assert_called_once_with("documents/receipts/480487019028416410")


def test_delete(mocker: MockType, document_data: dict[str, Any]):
    mock_delete = mocker.patch("moneysnake.document.http_delete")
    receipt = Receipt(**document_data)
    receipt.delete()
    assert receipt.id is None
    mock_delete.assert_called_once_with("documents/receipts/480487019028416410")


def test_list_all(mocker: MockType, document_data: dict[str, Any]):
    mock_paginate = mocker.patch("moneysnake.document.paginate")
    mock_paginate.return_value = [document_data]
    receipts = Receipt.list_all(contact_id=42)
    assert len(receipts) == 1
    assert mock_paginate.call_args[0][0] == "documents/receipts"
    assert "contact_id:42" in mock_paginate.call_args[1]["params"]["filter"]


def test_add_detail(document_data: dict[str, Any]):
    receipt = Receipt(**document_data)
    receipt.add_detail(ReceiptDetailsAttribute(description="Coffee", price="3.5"))
    assert len(receipt.details) == 2


def test_sync_endpoint():
    assert Receipt._sync_endpoint() == "documents/receipt"
