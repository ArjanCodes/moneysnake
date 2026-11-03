import importlib
from moneysnake.financial_mutation import FinancialMutation
from pytest_mock import MockType
from freezegun import freeze_time


def test_search_financial_mutations(mocker: MockType):
    """
    Test searching for financial mutations.
    """
    mock_http_get = mocker.patch("moneysnake.financial_mutation.paginate")

    # Mock response data
    mock_data = [
        {
            "id": "1",
            "amount": "100.00",
            "message": "Test 1",
            "date": "2023-01-01",
        },
        {
            "id": "2",
            "amount": "200.00",
            "message": "Test 2",
            "date": "2023-01-01",
        },
    ]
    mock_http_get.return_value = mock_data

    results = FinancialMutation.search(
        query_string="query:test", period="20230101", financial_account_id="123"
    )

    # Verify http_get was called with correct params
    expected_filter = "query:test,period:20230101..20230101,financial_account_id:123"
    mock_http_get.assert_called_once_with(
        "financial_mutations", params={"filter": expected_filter}
    )

    # Verify results are FinancialMutation objects
    assert len(results) == 2
    assert isinstance(results[0], FinancialMutation)
    assert results[0].id == 1
    assert results[0].amount == "100.00"
    assert results[1].id == 2


def test_search_financial_mutations_simple_period(mocker: MockType):
    """
    Test searching with a period that doesn't need formatting.
    """
    mock_http_get = mocker.patch("moneysnake.financial_mutation.paginate")
    mock_http_get.return_value = []

    FinancialMutation.search(
        query_string="query:test",
        period="202301",  # Month
    )

    expected_filter = "query:test,period:202301"
    mock_http_get.assert_called_once_with(
        "financial_mutations", params={"filter": expected_filter}
    )


@freeze_time("2023-10-25")
def test_search_financial_mutations_default_period(mocker: MockType):
    """
    Test searching with default period (current day).
    """
    # Reload the module within the frozen time context
    import moneysnake.financial_mutation

    importlib.reload(moneysnake.financial_mutation)
    from moneysnake.financial_mutation import FinancialMutation as FM

    mock_http_get = mocker.patch("moneysnake.financial_mutation.paginate")
    mock_http_get.return_value = []

    FM.search(query_string="query:test")

    # It should be formatted as a range because it is 8 chars
    expected_period = "20231025..20231025"
    expected_filter = f"query:test,period:{expected_period}"

    mock_http_get.assert_called_once_with(
        "financial_mutations", params={"filter": expected_filter}
    )


def test_search_default_period_uses_current_day_per_call(mocker: MockType):
    mock_paginate = mocker.patch("moneysnake.financial_mutation.paginate")
    mock_paginate.return_value = []

    with freeze_time("2024-03-01"):
        FinancialMutation.search()
    with freeze_time("2024-03-02"):
        FinancialMutation.search()

    filters = [c.kwargs["params"]["filter"] for c in mock_paginate.call_args_list]
    assert filters == [
        "period:20240301..20240301",
        "period:20240302..20240302",
    ]


def test_search_passes_query_string_through_unchanged(mocker: MockType):
    mock_paginate = mocker.patch("moneysnake.financial_mutation.paginate")
    mock_paginate.return_value = []

    FinancialMutation.search(query_string="state:open,amount:>100", period="202301")

    mock_paginate.assert_called_once_with(
        "financial_mutations",
        params={"filter": "state:open,amount:>100,period:202301"},
    )
