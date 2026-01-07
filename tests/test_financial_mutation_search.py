import importlib
import pytest
from pytest_mock import MockType
from freezegun import freeze_time
from moneysnake.financial_mutation import FinancialMutation


def test_search_financial_mutations(mocker: MockType):
    """
    Test searching for financial mutations.
    """
    mock_http_get = mocker.patch("moneysnake.financial_mutation.http_get")

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
    Test searching with a month period (YYYYMM format).
    """
    mock_http_get = mocker.patch("moneysnake.financial_mutation.http_get")
    mock_http_get.return_value = []

    FinancialMutation.search(
        query_string="query:test",
        period="202301",  # Month
    )

    expected_filter = "query:test,period:202301..202301"
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

    mock_http_get = mocker.patch("moneysnake.financial_mutation.http_get")
    mock_http_get.return_value = []

    FM.search(query_string="query:test")

    # It should be formatted as a range because it is 8 chars
    expected_period = "20231025..20231025"
    expected_filter = f"query:test,period:{expected_period}"

    mock_http_get.assert_called_once_with(
        "financial_mutations", params={"filter": expected_filter}
    )


# --- Tests for _parse_date ---


def test_parse_date_yyyymmdd():
    """Test parsing a valid YYYYMMDD date string."""
    result = FinancialMutation._parse_date("20231025")
    assert result is not None
    assert result.year == 2023
    assert result.month == 10
    assert result.day == 25


def test_parse_date_yyyymm():
    """Test parsing a valid YYYYMM date string."""
    result = FinancialMutation._parse_date("202310")
    assert result is not None
    assert result.year == 2023
    assert result.month == 10
    assert result.day == 1  # Default to first day of month


def test_parse_date_invalid():
    """Test parsing invalid date strings."""
    assert FinancialMutation._parse_date("invalid") is None
    assert FinancialMutation._parse_date("2023-10-25") is None
    assert FinancialMutation._parse_date("") is None
    assert FinancialMutation._parse_date("99999999") is None  # Invalid date


# --- Tests for _validate_period ---


class TestValidatePeriodPredefined:
    """Tests for predefined period values."""

    @pytest.mark.parametrize(
        "period",
        [
            "this_month",
            "prev_month",
            "next_month",
            "this_quarter",
            "prev_quarter",
            "next_quarter",
            "this_year",
            "prev_year",
            "next_year",
        ],
    )
    def test_predefined_periods(self, period: str):
        """Test that predefined periods are returned as-is."""
        result = FinancialMutation._validate_period(period)
        assert result == period


class TestValidatePeriodSingleDate:
    """Tests for single date period values."""

    def test_single_date_yyyymmdd(self):
        """Test that a single YYYYMMDD date is formatted as a range."""
        result = FinancialMutation._validate_period("20231025")
        assert result == "20231025..20231025"

    def test_single_date_yyyymm(self):
        """Test that a single YYYYMM date is formatted as a range."""
        result = FinancialMutation._validate_period("202310")
        assert result == "202310..202310"

    def test_single_date_invalid(self):
        """Test that invalid single dates raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            FinancialMutation._validate_period("invalid")
        assert "Invalid period format" in str(exc_info.value)

    def test_single_date_invalid_format(self):
        """Test that dates in wrong format raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            FinancialMutation._validate_period("2023-10-25")
        assert "Invalid period format" in str(exc_info.value)


class TestValidatePeriodRange:
    """Tests for date range period values."""

    def test_valid_range_yyyymmdd(self):
        """Test a valid YYYYMMDD..YYYYMMDD range."""
        result = FinancialMutation._validate_period("20231001..20231031")
        assert result == "20231001..20231031"

    def test_valid_range_yyyymm(self):
        """Test a valid YYYYMM..YYYYMM range."""
        result = FinancialMutation._validate_period("202301..202303")
        assert result == "202301..202303"

    def test_valid_range_same_date(self):
        """Test a range where start and end are the same."""
        result = FinancialMutation._validate_period("20231025..20231025")
        assert result == "20231025..20231025"

    def test_invalid_range_start_after_end(self):
        """Test that a range with start date after end date raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            FinancialMutation._validate_period("20231031..20231001")
        assert "start date '20231031' is later than end date '20231001'" in str(
            exc_info.value
        )

    def test_invalid_range_start_after_end_months(self):
        """Test that a month range with start after end raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            FinancialMutation._validate_period("202312..202301")
        assert "start date '202312' is later than end date '202301'" in str(
            exc_info.value
        )

    def test_invalid_range_bad_start_date(self):
        """Test that a range with invalid start date raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            FinancialMutation._validate_period("invalid..20231031")
        assert "Invalid start date format: 'invalid'" in str(exc_info.value)

    def test_invalid_range_bad_end_date(self):
        """Test that a range with invalid end date raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            FinancialMutation._validate_period("20231001..invalid")
        assert "Invalid end date format: 'invalid'" in str(exc_info.value)

    def test_invalid_range_too_many_parts(self):
        """Test that a range with too many parts raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            FinancialMutation._validate_period("20231001..20231015..20231031")
        assert "Invalid period range format" in str(exc_info.value)


class TestSearchWithPeriodValidation:
    """Integration tests for search with period validation."""

    def test_search_with_predefined_period(self, mocker: MockType):
        """Test search with a predefined period."""
        mock_http_get = mocker.patch("moneysnake.financial_mutation.http_get")
        mock_http_get.return_value = []

        FinancialMutation.search(period="this_month")

        mock_http_get.assert_called_once_with(
            "financial_mutations", params={"filter": "period:this_month"}
        )

    def test_search_with_date_range(self, mocker: MockType):
        """Test search with a date range period."""
        mock_http_get = mocker.patch("moneysnake.financial_mutation.http_get")
        mock_http_get.return_value = []

        FinancialMutation.search(period="20231001..20231031")

        mock_http_get.assert_called_once_with(
            "financial_mutations", params={"filter": "period:20231001..20231031"}
        )

    def test_search_with_invalid_period_raises(self, mocker: MockType):
        """Test that search with invalid period raises ValueError."""
        mocker.patch("moneysnake.financial_mutation.http_get")

        with pytest.raises(ValueError) as exc_info:
            FinancialMutation.search(period="invalid_period")
        assert "Invalid period format" in str(exc_info.value)

    def test_search_with_invalid_range_raises(self, mocker: MockType):
        """Test that search with invalid date range raises ValueError."""
        mocker.patch("moneysnake.financial_mutation.http_get")

        with pytest.raises(ValueError) as exc_info:
            FinancialMutation.search(period="20231031..20231001")
        assert "start date" in str(exc_info.value)
        assert "later than end date" in str(exc_info.value)
