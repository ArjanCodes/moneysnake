import pytest
from pytest_mock import MockType
from moneysnake.tax_rate import TaxRate

type TaxRateData = list[dict[str, str | int | float | bool | None]]


@pytest.fixture(name="tax_rates_data")
def fixture_tax_rates_data() -> TaxRateData:
    return [
        {
            "id": "123",
            "administration_id": 1,
            "name": "BTW 21%",
            "percentage": 21.0,
            "tax_rate_type": "sales_invoice",
            "show_tax": True,
            "country": "NL",
            "active": True,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z",
        },
        {
            "id": "456",
            "administration_id": 1,
            "name": "BTW 0%",
            "percentage": 0.0,
            "tax_rate_type": "sales_invoice",
            "show_tax": True,
            "country": "DE",
            "active": True,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z",
        },
    ]


def test_list_all_rates(mocker: MockType, tax_rates_data: TaxRateData):
    mock_get = mocker.patch("moneysnake.tax_rate.http_get", return_value=tax_rates_data)

    rates = TaxRate.list_all_rates()

    assert len(rates) == 2
    assert rates[0].name == "BTW 21%"
    assert rates[1].country == "DE"
    mock_get.assert_called_with("tax_rates")


def test_all_sales(mocker: MockType, tax_rates_data: TaxRateData):
    mock_get = mocker.patch("moneysnake.tax_rate.http_get", return_value=tax_rates_data)

    rates = TaxRate.list_sales_rates()

    assert len(rates) == 2
    mock_get.assert_called_with("tax_rates?filter=tax_rate_type:sales_invoice")


def test_find_sales_by_country(mocker: MockType, tax_rates_data: TaxRateData):
    mock_get = mocker.patch(
        "moneysnake.tax_rate.http_get", return_value=[tax_rates_data[0]]
    )

    rates = TaxRate.find_sales_rate_by_country("NL")

    assert len(rates) == 1
    assert rates[0].country == "NL"

    mock_get.assert_called_with(
        "tax_rates?filter=country:NL,tax_rate_type:sales_invoice"
    )
