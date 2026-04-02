from pytest_mock import MockType
from moneysnake.client import paginate


def test_paginate_single_page(mocker: MockType):
    """When results fit in one page, return them all."""
    mock_get = mocker.patch(
        "moneysnake.client.http_get", return_value=[{"id": 1}, {"id": 2}]
    )

    results = paginate("contacts", per_page=100)

    assert len(results) == 2
    mock_get.assert_called_once_with("contacts", params={"per_page": 100, "page": 1})


def test_paginate_multiple_pages(mocker: MockType):
    """When first page is full, fetch next page."""
    page1 = [{"id": i} for i in range(3)]
    page2 = [{"id": 3}]
    mock_get = mocker.patch("moneysnake.client.http_get", side_effect=[page1, page2])

    results = paginate("contacts", per_page=3)

    assert len(results) == 4
    assert mock_get.call_count == 2


def test_paginate_empty_result(mocker: MockType):
    """Empty list returns empty."""
    mocker.patch("moneysnake.client.http_get", return_value=[])

    results = paginate("contacts")

    assert results == []


def test_paginate_passes_params(mocker: MockType):
    """Extra params are forwarded to http_get."""
    mocker.patch("moneysnake.client.http_get", return_value=[])

    paginate("contacts", params={"filter": "name:test"}, per_page=50)

    from moneysnake.client import http_get

    http_get.assert_called_once_with(
        "contacts", params={"filter": "name:test", "per_page": 50, "page": 1}
    )


def test_paginate_non_list_response(mocker: MockType):
    """If API returns a non-list, wrap it."""
    mocker.patch("moneysnake.client.http_get", return_value={"id": 1})

    results = paginate("contacts")

    assert results == [{"id": 1}]
