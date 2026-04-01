from typing import Any

import pytest
from pytest_mock import MockType

from moneysnake.contact import Contact
from moneysnake.external_sales_invoice import ExternalSalesInvoice
from moneysnake.financial_mutation import FinancialMutation
from moneysnake.sales_invoice import SalesInvoice


@pytest.fixture(name="sync_ids")
def fixture_sync_ids() -> list[dict[str, Any]]:
    return [
        {"id": 1, "version": 100},
        {"id": 2, "version": 200},
        {"id": 3, "version": 300},
    ]


class TestSyncList:
    def test_sync_list_contacts(self, mocker: MockType, sync_ids: list[dict[str, Any]]):
        mock_paginate = mocker.patch("moneysnake.model.paginate", return_value=sync_ids)
        result = Contact.sync_list()
        assert len(result) == 3
        assert result[0]["id"] == 1
        mock_paginate.assert_called_once_with("contacts/synchronization", params=None)

    def test_sync_list_with_filter(self, mocker: MockType, sync_ids: list[dict[str, Any]]):
        mock_paginate = mocker.patch("moneysnake.model.paginate", return_value=sync_ids)
        Contact.sync_list(filter="state:active")
        mock_paginate.assert_called_once_with(
            "contacts/synchronization", params={"filter": "state:active"}
        )

    def test_sync_list_sales_invoices(self, mocker: MockType, sync_ids: list[dict[str, Any]]):
        mock_paginate = mocker.patch("moneysnake.model.paginate", return_value=sync_ids)
        result = SalesInvoice.sync_list()
        assert len(result) == 3
        mock_paginate.assert_called_once_with("sales_invoices/synchronization", params=None)

    def test_sync_list_external_sales_invoices(self, mocker: MockType, sync_ids: list[dict[str, Any]]):
        mock_paginate = mocker.patch("moneysnake.model.paginate", return_value=sync_ids)
        ExternalSalesInvoice.sync_list()
        mock_paginate.assert_called_once_with(
            "external_sales_invoices/synchronization", params=None
        )

    def test_sync_list_financial_mutations(self, mocker: MockType, sync_ids: list[dict[str, Any]]):
        mock_paginate = mocker.patch("moneysnake.model.paginate", return_value=sync_ids)
        FinancialMutation.sync_list()
        mock_paginate.assert_called_once_with(
            "financial_mutations/synchronization", params=None
        )


class TestSyncFetch:
    def test_sync_fetch_contacts(self, mocker: MockType):
        contact_data = [
            {"id": 1, "company_name": "Acme"},
            {"id": 2, "company_name": "Globex"},
        ]
        mock_post = mocker.patch("moneysnake.model.http_post", return_value=contact_data)
        result = Contact.sync_fetch([1, 2])
        assert len(result) == 2
        assert isinstance(result[0], Contact)
        assert result[0].company_name == "Acme"
        mock_post.assert_called_once_with(
            "contacts/synchronization", data={"ids": [1, 2]}
        )

    def test_sync_fetch_sales_invoices(self, mocker: MockType):
        invoice_data = [{"id": 1, "state": "draft"}, {"id": 2, "state": "open"}]
        mocker.patch("moneysnake.model.http_post", return_value=invoice_data)
        result = SalesInvoice.sync_fetch([1, 2])
        assert len(result) == 2
        assert isinstance(result[0], SalesInvoice)

    def test_sync_fetch_max_100(self):
        with pytest.raises(ValueError, match="maximum of 100"):
            Contact.sync_fetch(list(range(101)))

    def test_sync_fetch_non_list_response(self, mocker: MockType):
        mocker.patch("moneysnake.model.http_post", return_value={})
        result = Contact.sync_fetch([1])
        assert result == []

    def test_sync_fetch_empty_list(self, mocker: MockType):
        mocker.patch("moneysnake.model.http_post", return_value=[])
        result = Contact.sync_fetch([])
        assert result == []
