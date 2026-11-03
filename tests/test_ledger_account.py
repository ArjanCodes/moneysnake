from typing import Any

import httpx
import pytest
from pytest_mock import MockType

from moneysnake import LedgerAccount, MoneybirdNotFoundError


@pytest.fixture(name="ledger_account_data")
def fixture_ledger_account_data() -> dict[str, Any]:
    return {
        "id": "502768552417166930",
        "administration_id": 123,
        "name": "new name",
        "account_type": "revenue",
        "account_id": "80829",
        "parent_id": None,
        "active": True,
        "created_at": "2026-11-03T09:17:57.258Z",
        "updated_at": "2026-11-03T09:17:57.271Z",
        "allowed_document_types": ["sales_invoice"],
        "taxonomy_item": None,
        "financial_account_id": None,
    }


def test_list_all_makes_one_request(
    mocker: MockType, ledger_account_data: dict[str, Any]
):
    second = {**ledger_account_data, "id": "502768552417166931", "name": "Costs"}
    mock_get = mocker.patch(
        "moneysnake.ledger_account.http_get",
        return_value=[ledger_account_data, second],
    )

    accounts = LedgerAccount.list_all()

    mock_get.assert_called_once_with("ledger_accounts")
    assert len(accounts) == 2
    assert all(isinstance(account, LedgerAccount) for account in accounts)
    assert accounts[0].id == 502768552417166930
    assert accounts[0].account_type == "revenue"
    assert accounts[0].account_id == "80829"
    assert accounts[0].allowed_document_types == ["sales_invoice"]
    assert accounts[0].taxonomy_item is None
    assert accounts[1].name == "Costs"


def test_list_all_sends_no_page_params(
    mocker: MockType, ledger_account_data: dict[str, Any]
):
    response = httpx.Response(
        200,
        json=[ledger_account_data],
        request=httpx.Request("GET", "http://test"),
    )
    mock_request = mocker.patch(
        "moneysnake.client.httpx.request", return_value=response
    )

    accounts = LedgerAccount.list_all()

    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert args[1].endswith("/ledger_accounts")
    assert kwargs["params"] is None
    assert accounts[0].name == "new name"


def test_find_by_id_returns_model(
    mocker: MockType, ledger_account_data: dict[str, Any]
):
    mock_get = mocker.patch(
        "moneysnake.model.http_get", return_value=ledger_account_data
    )

    account = LedgerAccount.find_by_id(502768552417166930)

    mock_get.assert_called_once_with("ledger_accounts/502768552417166930")
    assert isinstance(account, LedgerAccount)
    assert account.name == "new name"
    assert account.administration_id == 123
    assert account.active is True
    assert account.created_at == "2026-11-03T09:17:57.258Z"


def test_find_by_id_raises_not_found(mocker: MockType):
    response = httpx.Response(
        404, text="Not found", request=httpx.Request("GET", "http://test")
    )
    mocker.patch("moneysnake.client.httpx.request", return_value=response)

    with pytest.raises(MoneybirdNotFoundError) as exc_info:
        LedgerAccount.find_by_id(1)

    assert exc_info.value.status_code == 404


def test_defaults():
    account = LedgerAccount()

    assert account.allowed_document_types == []
    assert account.taxonomy_item is None
