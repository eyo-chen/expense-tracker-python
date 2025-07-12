import pytest
from datetime import datetime, timezone
from pymongo import MongoClient
from adapters.historical_portfolio import HistoricalPortfolioRepository
from domain.historical_portfolio import HistoricalPortfolio, HistoricalHolding
from domain.enum import StockType


@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient("mongodb://localhost:27015")
    yield client
    client.drop_database("test_stock_db")
    client.close()


@pytest.fixture(scope="module")
def historical_portfolio_repository(mongo_client):
    return HistoricalPortfolioRepository(mongo_client, database_name="test_stock_db")


@pytest.fixture(scope="function", autouse=True)
def clear_collection(historical_portfolio_repository):
    historical_portfolio_repository.collection.delete_many({})


class TestHistoricalPortfolioRepository:
    def test_update_new_historical_portfolio(self, historical_portfolio_repository):
        # Arrange
        date = datetime.now(timezone.utc)
        created_at = datetime.now(timezone.utc)
        historical_portfolio = HistoricalPortfolio(
            user_id=1,
            date=date,
            portfolio_value=1000.0,
            cash_balance=1000.0,
            money_in=1000.0,
            holdings_value=1000.0,
            holdings_value_breakdown=[
                HistoricalHolding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_value=1500.0)
            ],
            gain=0.0,
            roi=0.0,
            created_at=created_at,
            updated_at=created_at,
        )

        # Action
        historical_portfolio_repository.update(historical_portfolio)

        # Assertion
        result = historical_portfolio_repository.collection.find_one({"user_id": 1, "date": date.strftime("%Y-%m-%d")})
        assert result["user_id"] == historical_portfolio.user_id
        assert result["date"] == historical_portfolio.date.strftime("%Y-%m-%d")
        assert result["portfolio_value"] == historical_portfolio.portfolio_value
        assert result["cash_balance"] == historical_portfolio.cash_balance
        assert result["money_in"] == historical_portfolio.money_in
        assert result["holdings_value"] == historical_portfolio.holdings_value
        assert len(result["holdings_value_breakdown"]) == 1
        assert result["holdings_value_breakdown"][0]["symbol"] == "AAPL"
        assert result["holdings_value_breakdown"][0]["shares"] == 10
        assert result["holdings_value_breakdown"][0]["stock_type"] == StockType.STOCKS.value
        assert result["holdings_value_breakdown"][0]["total_value"] == 1500.0

    def test_update_existing_historical_portfolio(self, historical_portfolio_repository):
        # Arrange
        date = datetime.now(timezone.utc)
        created_at = datetime.now(timezone.utc)
        initial_historical_portfolio = HistoricalPortfolio(
            user_id=1,
            date=date,
            portfolio_value=1000.0,
            cash_balance=1000.0,
            money_in=1000.0,
            holdings_value=1000.0,
            holdings_value_breakdown=[
                HistoricalHolding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_value=1500.0)
            ],
            gain=0.0,
            roi=0.0,
            created_at=created_at,
            updated_at=created_at,
        )
        historical_portfolio_repository.collection.insert_one(initial_historical_portfolio.as_dict())

        updated_portfolio_value = 2000.0
        updated_cash_balance = 2000.0
        updated_cash_in = 2000.0
        updated_holdings_value = 2000.0
        updated_holdings_value_breakdown = [
            HistoricalHolding(symbol="AAPL", shares=20, stock_type=StockType.STOCKS, total_value=3000.0)
        ]
        updated_gain = 1000.0
        updated_roi = 0.5
        updated_historical_portfolio = HistoricalPortfolio(
            user_id=1,
            date=date,
            portfolio_value=updated_portfolio_value,
            cash_balance=updated_cash_balance,
            money_in=updated_cash_in,
            holdings_value=updated_holdings_value,
            holdings_value_breakdown=updated_holdings_value_breakdown,
            gain=updated_gain,
            roi=updated_roi,
            created_at=created_at,
            updated_at=created_at,
        )

        # Action
        historical_portfolio_repository.update(updated_historical_portfolio)

        # Assertion
        result = historical_portfolio_repository.collection.find_one({"user_id": 1, "date": date.strftime("%Y-%m-%d")})
        assert result is not None
        assert result["user_id"] == updated_historical_portfolio.user_id
        assert result["date"] == updated_historical_portfolio.date.strftime("%Y-%m-%d")
        assert result["portfolio_value"] == updated_historical_portfolio.portfolio_value
        assert result["cash_balance"] == updated_historical_portfolio.cash_balance
        assert result["money_in"] == updated_historical_portfolio.money_in
        assert result["holdings_value"] == updated_historical_portfolio.holdings_value
        assert len(result["holdings_value_breakdown"]) == 1
        assert result["holdings_value_breakdown"][0]["symbol"] == "AAPL"
        assert result["holdings_value_breakdown"][0]["shares"] == 20
        assert result["holdings_value_breakdown"][0]["stock_type"] == StockType.STOCKS.value
        assert result["holdings_value_breakdown"][0]["total_value"] == 3000.0

    def test_get_by_user_and_date_range_empty_result(self, historical_portfolio_repository):
        # Arrange
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Action
        result = historical_portfolio_repository.get_by_user_and_date_range(1, start_date, end_date)

        # Assertion
        assert result == []

    def test_get_by_user_and_date_range_single_portfolio(self, historical_portfolio_repository):
        # Arrange
        date = datetime(2024, 1, 15, tzinfo=timezone.utc)
        created_at = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        historical_portfolio = HistoricalPortfolio(
            user_id=1,
            date=date,
            portfolio_value=1500.0,
            cash_balance=500.0,
            money_in=1000.0,
            holdings_value=1000.0,
            holdings_value_breakdown=[
                HistoricalHolding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_value=800.0),
                HistoricalHolding(symbol="GOOGL", shares=5, stock_type=StockType.STOCKS, total_value=200.0),
            ],
            gain=500.0,
            roi=0.5,
            created_at=created_at,
            updated_at=created_at,
        )
        historical_portfolio_repository.update(historical_portfolio)

        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Action
        result = historical_portfolio_repository.get_by_user_and_date_range(1, start_date, end_date)

        # Assertion
        assert len(result) == 1
        portfolio = result[0]
        assert portfolio.user_id == 1
        assert portfolio.date.date() == date.date()
        assert portfolio.portfolio_value == 1500.0
        assert portfolio.cash_balance == 500.0
        assert portfolio.money_in == 1000.0
        assert portfolio.holdings_value == 1000.0
        assert portfolio.gain == 500.0
        assert portfolio.roi == 0.5
        assert len(portfolio.holdings_value_breakdown) == 2

        holdings = portfolio.holdings_value_breakdown
        assert holdings[0].symbol == "AAPL"
        assert holdings[0].shares == 10
        assert holdings[0].stock_type == StockType.STOCKS
        assert holdings[0].total_value == 800.0
        assert holdings[1].symbol == "GOOGL"
        assert holdings[1].shares == 5
        assert holdings[1].stock_type == StockType.STOCKS
        assert holdings[1].total_value == 200.0

    def test_get_by_user_and_date_range_multiple_portfolios(self, historical_portfolio_repository):
        # Arrange
        created_at = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Create three portfolios for different dates
        dates = [
            datetime(2024, 1, 10, tzinfo=timezone.utc),
            datetime(2024, 1, 15, tzinfo=timezone.utc),
            datetime(2024, 1, 20, tzinfo=timezone.utc),
        ]

        for i, date in enumerate(dates):
            portfolio = HistoricalPortfolio(
                user_id=1,
                date=date,
                portfolio_value=1000.0 + (i * 100),
                cash_balance=500.0 + (i * 50),
                money_in=1000.0,
                holdings_value=500.0 + (i * 50),
                holdings_value_breakdown=[
                    HistoricalHolding(
                        symbol="AAPL", shares=10 + i, stock_type=StockType.STOCKS, total_value=500.0 + (i * 50)
                    )
                ],
                gain=i * 100,
                roi=i * 0.1,
                created_at=created_at,
                updated_at=created_at,
            )
            historical_portfolio_repository.update(portfolio)

        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Action
        result = historical_portfolio_repository.get_by_user_and_date_range(1, start_date, end_date)

        # Assertion
        assert len(result) == 3

        # Verify results are sorted by date (ascending)
        for i, portfolio in enumerate(result):
            assert portfolio.date.date() == dates[i].date()
            assert portfolio.portfolio_value == 1000.0 + (i * 100)
            assert portfolio.cash_balance == 500.0 + (i * 50)
            assert portfolio.holdings_value == 500.0 + (i * 50)
            assert portfolio.gain == i * 100
            assert portfolio.roi == i * 0.1

    def test_get_by_user_and_date_range_date_boundary(self, historical_portfolio_repository):
        # Arrange
        created_at = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Create portfolios on boundary dates and outside range
        portfolios_data = [
            (datetime(2024, 1, 5, tzinfo=timezone.utc), 1000.0),  # Before range
            (datetime(2024, 1, 10, tzinfo=timezone.utc), 1100.0),  # Start date (included)
            (datetime(2024, 1, 15, tzinfo=timezone.utc), 1200.0),  # Within range
            (datetime(2024, 1, 20, tzinfo=timezone.utc), 1300.0),  # End date (included)
            (datetime(2024, 1, 25, tzinfo=timezone.utc), 1400.0),  # After range
        ]

        for date, value in portfolios_data:
            portfolio = HistoricalPortfolio(
                user_id=1,
                date=date,
                portfolio_value=value,
                cash_balance=500.0,
                money_in=1000.0,
                holdings_value=500.0,
                holdings_value_breakdown=[
                    HistoricalHolding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_value=500.0)
                ],
                gain=100.0,
                roi=0.1,
                created_at=created_at,
                updated_at=created_at,
            )
            historical_portfolio_repository.update(portfolio)

        start_date = datetime(2024, 1, 10, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 20, tzinfo=timezone.utc)

        # Action
        result = historical_portfolio_repository.get_by_user_and_date_range(1, start_date, end_date)

        # Assertion
        assert len(result) == 3
        expected_values = [1100.0, 1200.0, 1300.0]
        for i, portfolio in enumerate(result):
            assert portfolio.portfolio_value == expected_values[i]

    def test_get_by_user_and_date_range_different_users(self, historical_portfolio_repository):
        # Arrange
        date = datetime(2024, 1, 15, tzinfo=timezone.utc)
        created_at = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        # Create portfolios for different users
        for user_id in [1, 2, 3]:
            portfolio = HistoricalPortfolio(
                user_id=user_id,
                date=date,
                portfolio_value=1000.0 * user_id,
                cash_balance=500.0 * user_id,
                money_in=1000.0,
                holdings_value=500.0 * user_id,
                holdings_value_breakdown=[
                    HistoricalHolding(
                        symbol="AAPL", shares=10 * user_id, stock_type=StockType.STOCKS, total_value=500.0 * user_id
                    )
                ],
                gain=100.0 * user_id,
                roi=0.1 * user_id,
                created_at=created_at,
                updated_at=created_at,
            )
            historical_portfolio_repository.update(portfolio)

        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        # Action
        result = historical_portfolio_repository.get_by_user_and_date_range(2, start_date, end_date)

        # Assertion
        assert len(result) == 1
        portfolio = result[0]
        assert portfolio.user_id == 2
        assert portfolio.portfolio_value == 2000.0
        assert portfolio.cash_balance == 1000.0
