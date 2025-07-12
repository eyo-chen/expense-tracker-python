import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, ANY, patch
from usecase.historical_portfolio import HistoricalPortfolioUsecase
from domain.portfolio import Portfolio, Holding
from domain.enum import StockType, DateOption
from domain.historical_portfolio import HistoricalPortfolio, HistoricalHolding


@pytest.fixture
def create_usecase_fixture():
    """Fixture for testing create method"""
    historical_portfolio_repo = Mock()
    portfolio_repo = Mock()
    usecase = HistoricalPortfolioUsecase(
        historical_portfolio_repo=historical_portfolio_repo, portfolio_repo=portfolio_repo
    )
    return usecase, historical_portfolio_repo, portfolio_repo


@pytest.fixture
def get_portfolio_value_fixture():
    """Fixture for testing get_portfolio_value method"""
    historical_portfolio_repo = Mock()
    portfolio_repo = Mock()
    usecase = HistoricalPortfolioUsecase(
        historical_portfolio_repo=historical_portfolio_repo, portfolio_repo=portfolio_repo
    )
    return usecase, historical_portfolio_repo


class TestHistoricalPortfolioCreate:
    @patch.object(HistoricalPortfolioUsecase, "_get_stock_price")
    def test_create_no_portfolio(self, mock_get_stock_price, create_usecase_fixture):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = create_usecase_fixture
        user_id = 1
        date = datetime(2025, 7, 5)
        portfolio_repo.get.return_value = None

        # Act
        usecase.create(user_id, date)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        historical_portfolio_repo.assert_not_called()

    @patch.object(HistoricalPortfolioUsecase, "_get_stock_price")
    def test_create_empty_portfolio(self, mock_get_stock_price, create_usecase_fixture):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = create_usecase_fixture
        user_id = 1
        date = datetime(2025, 7, 5)
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=0.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = portfolio

        # Act
        usecase.create(user_id, date)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        historical_portfolio_repo.assert_not_called()

    @patch.object(HistoricalPortfolioUsecase, "_get_stock_price")
    def test_create_no_valid_holdings(self, mock_get_stock_price, create_usecase_fixture):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = create_usecase_fixture
        user_id = 1
        date = datetime(2025, 7, 5)
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=2000.0,
            holdings=[Holding(symbol="AAPL", shares=0, stock_type=StockType.STOCKS, total_cost=0.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = portfolio

        # Act
        usecase.create(user_id, date)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        historical_portfolio_repo.assert_not_called()

    @patch.object(HistoricalPortfolioUsecase, "_get_stock_price")
    def test_create_with_valid_holdings(self, mock_get_stock_price, create_usecase_fixture):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = create_usecase_fixture
        user_id = 1
        date = datetime(2025, 7, 5)
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=2000.0,
            holdings=[
                Holding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_cost=1500.0),
                Holding(symbol="SPY", shares=5, stock_type=StockType.ETF, total_cost=1000.0),
            ],
            created_at=ANY,
            updated_at=ANY,
        )
        mock_get_stock_price.return_value = {"AAPL": 200.0, "SPY": 400.0}
        portfolio_repo.get.return_value = portfolio

        stock_value = 10 * 200 + 5 * 400
        historical_portfolio = HistoricalPortfolio(
            user_id=user_id,
            date=date.replace(day=1),
            portfolio_value=stock_value + portfolio.cash_balance,
            cash_balance=portfolio.cash_balance,
            money_in=portfolio.total_money_in,
            holdings_value=stock_value,
            holdings_value_breakdown=[
                HistoricalHolding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_value=10 * 200),
                HistoricalHolding(symbol="SPY", shares=5, stock_type=StockType.ETF, total_value=5 * 400),
            ],
            gain=stock_value + portfolio.cash_balance - portfolio.total_money_in,
            roi=round(
                ((stock_value + portfolio.cash_balance - portfolio.total_money_in) / portfolio.total_money_in) * 100, 2
            ),
            created_at=ANY,
            updated_at=ANY,
        )

        # Act
        usecase.create(user_id, date)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_called_once_with(stock_info=[("AAPL", StockType.STOCKS), ("SPY", StockType.ETF)])
        historical_portfolio_repo.update.assert_called_once_with(historical_portfolio)


class TestGetPortfolioValue:
    def test_get_portfolio_value_no_historical_data(self, get_portfolio_value_fixture):
        # Arrange
        usecase, historical_portfolio_repo = get_portfolio_value_fixture
        user_id = 1
        date_option = DateOption.THREE_MONTHS
        historical_portfolio_repo.get_by_user_and_date_range.return_value = []

        # Act
        result = usecase.get_portfolio_value(user_id, date_option)

        # Assert
        assert result == {"date": [], "values": []}
        historical_portfolio_repo.get_by_user_and_date_range.assert_called_once()

    def test_get_portfolio_value_three_months(self, get_portfolio_value_fixture):
        # Arrange
        usecase, historical_portfolio_repo = get_portfolio_value_fixture
        user_id = 1
        date_option = DateOption.THREE_MONTHS

        historical_portfolios = [
            HistoricalPortfolio(
                user_id=user_id,
                date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                portfolio_value=1000.0,
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=900.0,
                holdings_value_breakdown=[],
                gain=100.0,
                roi=11.11,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            HistoricalPortfolio(
                user_id=user_id,
                date=datetime(2024, 2, 1, tzinfo=timezone.utc),
                portfolio_value=1100.0,
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=1000.0,
                holdings_value_breakdown=[],
                gain=200.0,
                roi=22.22,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            HistoricalPortfolio(
                user_id=user_id,
                date=datetime(2024, 3, 1, tzinfo=timezone.utc),
                portfolio_value=1200.0,
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=1100.0,
                holdings_value_breakdown=[],
                gain=300.0,
                roi=33.33,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]
        historical_portfolio_repo.get_by_user_and_date_range.return_value = historical_portfolios

        # Act
        result = usecase.get_portfolio_value(user_id, date_option)

        # Assert
        expected = {"date": ["Jan 2024", "Feb 2024", "Mar 2024"], "values": [1000.0, 1100.0, 1200.0]}
        assert result == expected

    def test_get_portfolio_value_one_year(self, get_portfolio_value_fixture):
        # Arrange
        usecase, historical_portfolio_repo = get_portfolio_value_fixture
        user_id = 1
        date_option = DateOption.ONE_YEAR

        # Create 12 months of data
        historical_portfolios = []
        for month in range(1, 13):
            portfolio = HistoricalPortfolio(
                user_id=user_id,
                date=datetime(2024, month, 1, tzinfo=timezone.utc),
                portfolio_value=1000.0 + (month * 100),
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=900.0 + (month * 100),
                holdings_value_breakdown=[],
                gain=100.0 + (month * 100),
                roi=11.11,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            historical_portfolios.append(portfolio)

        historical_portfolio_repo.get_by_user_and_date_range.return_value = historical_portfolios

        # Act
        result = usecase.get_portfolio_value(user_id, date_option)

        # Assert
        expected_result = {
            "date": [
                "Jan 2024",
                "Feb 2024",
                "Mar 2024",
                "Apr 2024",
                "May 2024",
                "Jun 2024",
                "Jul 2024",
                "Aug 2024",
                "Sep 2024",
                "Oct 2024",
                "Nov 2024",
                "Dec 2024",
            ],
            "values": [
                1100.0,
                1200.0,
                1300.0,
                1400.0,
                1500.0,
                1600.0,
                1700.0,
                1800.0,
                1900.0,
                2000.0,
                2100.0,
                2200.0,
            ],
        }

        assert result == expected_result

    def test_get_portfolio_value_two_years_sampling(self, get_portfolio_value_fixture):
        # Arrange
        usecase, historical_portfolio_repo = get_portfolio_value_fixture
        user_id = 1
        date_option = DateOption.TWO_YEARS

        # Create 24 months of data (should be sampled to 12 points)
        historical_portfolios = []
        for month in range(1, 25):
            year = 2023 if month <= 12 else 2024
            month_in_year = month if month <= 12 else month - 12
            portfolio = HistoricalPortfolio(
                user_id=user_id,
                date=datetime(year, month_in_year, 1, tzinfo=timezone.utc),
                portfolio_value=1000.0 + (month * 50),
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=900.0 + (month * 50),
                holdings_value_breakdown=[],
                gain=100.0 + (month * 50),
                roi=11.11,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            historical_portfolios.append(portfolio)

        historical_portfolio_repo.get_by_user_and_date_range.return_value = historical_portfolios

        # Act
        result = usecase.get_portfolio_value(user_id, date_option)

        # Assert
        # Should sample every 2nd month (24 // 12 = 2) and limit to 12 points
        expected_result = {
            "date": [
                "Jan 2023",
                "Mar 2023",
                "May 2023",
                "Jul 2023",
                "Sep 2023",
                "Nov 2023",
                "Jan 2024",
                "Mar 2024",
                "May 2024",
                "Jul 2024",
                "Sep 2024",
                "Nov 2024",
            ],
            "values": [
                1050.0,
                1150.0,
                1250.0,
                1350.0,
                1450.0,
                1550.0,
                1650.0,
                1750.0,
                1850.0,
                1950.0,
                2050.0,
                2150.0,
            ],
        }

        assert result == expected_result

    def test_get_portfolio_value_three_years_sampling(self, get_portfolio_value_fixture):
        # Arrange
        usecase, historical_portfolio_repo = get_portfolio_value_fixture
        user_id = 1
        date_option = DateOption.THREE_YEARS

        # Create 36 months of data (should be sampled to 12 points)
        historical_portfolios = []
        for month in range(1, 37):
            if month <= 12:
                year, month_in_year = 2022, month
            elif month <= 24:
                year, month_in_year = 2023, month - 12
            else:
                year, month_in_year = 2024, month - 24

            portfolio = HistoricalPortfolio(
                user_id=user_id,
                date=datetime(year, month_in_year, 1, tzinfo=timezone.utc),
                portfolio_value=1000.0 + (month * 30),
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=900.0 + (month * 30),
                holdings_value_breakdown=[],
                gain=100.0 + (month * 30),
                roi=11.11,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            historical_portfolios.append(portfolio)

        historical_portfolio_repo.get_by_user_and_date_range.return_value = historical_portfolios

        # Act
        result = usecase.get_portfolio_value(user_id, date_option)

        # Assert
        # Should sample every 3rd month (36 // 12 = 3) and limit to 12 points
        expected_result = {
            "date": [
                "Jan 2022",
                "Apr 2022",
                "Jul 2022",
                "Oct 2022",
                "Jan 2023",
                "Apr 2023",
                "Jul 2023",
                "Oct 2023",
                "Jan 2024",
                "Apr 2024",
                "Jul 2024",
                "Oct 2024",
            ],
            "values": [
                1030.0,
                1120.0,
                1210.0,
                1300.0,
                1390.0,
                1480.0,
                1570.0,
                1660.0,
                1750.0,
                1840.0,
                1930.0,
                2020.0,
            ],
        }

        assert result == expected_result

    def test_get_portfolio_value_all_time(self, get_portfolio_value_fixture):
        # Arrange
        usecase, historical_portfolio_repo = get_portfolio_value_fixture
        user_id = 1
        date_option = DateOption.ALL_TIME

        # Create 60 months of data (should be sampled to 12 points)
        historical_portfolios = []
        for month in range(1, 61):
            portfolio = HistoricalPortfolio(
                user_id=user_id,
                date=datetime(2020 + (month - 1) // 12, ((month - 1) % 12) + 1, 1, tzinfo=timezone.utc),
                portfolio_value=1000.0 + (month * 20),
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=900.0 + (month * 20),
                holdings_value_breakdown=[],
                gain=100.0 + (month * 20),
                roi=11.11,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            historical_portfolios.append(portfolio)

        historical_portfolio_repo.get_by_user_and_date_range.return_value = historical_portfolios

        # Act
        result = usecase.get_portfolio_value(user_id, date_option)

        # Assert
        # Should sample every 5th month (60 // 12 = 5) and limit to 12 points
        expected_result = {
            "date": [
                "Jan 2020",
                "Jun 2020",
                "Nov 2020",
                "Apr 2021",
                "Sep 2021",
                "Feb 2022",
                "Jul 2022",
                "Dec 2022",
                "May 2023",
                "Oct 2023",
                "Mar 2024",
                "Aug 2024",
            ],
            "values": [
                1020.0,
                1120.0,
                1220.0,
                1320.0,
                1420.0,
                1520.0,
                1620.0,
                1720.0,
                1820.0,
                1920.0,
                2020.0,
                2120.0,
            ],
        }

        assert result == expected_result

    def test_get_portfolio_value_small_dataset_no_sampling(self, get_portfolio_value_fixture):
        # Arrange
        usecase, historical_portfolio_repo = get_portfolio_value_fixture
        user_id = 1
        date_option = DateOption.TWO_YEARS

        # Create only 8 months of data (should use all without sampling)
        historical_portfolios = []
        for month in range(1, 9):
            portfolio = HistoricalPortfolio(
                user_id=user_id,
                date=datetime(2024, month, 1, tzinfo=timezone.utc),
                portfolio_value=1000.0 + (month * 100),
                cash_balance=100.0,
                money_in=900.0,
                holdings_value=900.0 + (month * 100),
                holdings_value_breakdown=[],
                gain=100.0 + (month * 100),
                roi=11.11,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            historical_portfolios.append(portfolio)

        historical_portfolio_repo.get_by_user_and_date_range.return_value = historical_portfolios

        # Act
        result = usecase.get_portfolio_value(user_id, date_option)

        # Assert
        # Should use all 8 data points without sampling
        expected_result = {
            "date": [
                "Jan 2024",
                "Feb 2024",
                "Mar 2024",
                "Apr 2024",
                "May 2024",
                "Jun 2024",
                "Jul 2024",
                "Aug 2024",
            ],
            "values": [1100.0, 1200.0, 1300.0, 1400.0, 1500.0, 1600.0, 1700.0, 1800.0],
        }

        assert result == expected_result
