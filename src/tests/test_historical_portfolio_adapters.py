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
            cash_in=1000.0,
            holdings_value=1000.0,
            holdings_value_breakdown=[HistoricalHolding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_value=1500.0)],
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
        assert result["cash_in"] == historical_portfolio.cash_in
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
            cash_in=1000.0,
            holdings_value=1000.0,
            holdings_value_breakdown=[HistoricalHolding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_value=1500.0)],
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
        updated_holdings_value_breakdown = [HistoricalHolding(symbol="AAPL", shares=20, stock_type=StockType.STOCKS, total_value=3000.0)]
        updated_gain = 1000.0
        updated_roi = 0.5
        updated_historical_portfolio = HistoricalPortfolio(
            user_id=1,
            date=date,
            portfolio_value=updated_portfolio_value,
            cash_balance=updated_cash_balance,
            cash_in=updated_cash_in,
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
        assert result["cash_in"] == updated_historical_portfolio.cash_in
        assert result["holdings_value"] == updated_historical_portfolio.holdings_value
        assert len(result["holdings_value_breakdown"]) == 1
        assert result["holdings_value_breakdown"][0]["symbol"] == "AAPL"
        assert result["holdings_value_breakdown"][0]["shares"] == 20
        assert result["holdings_value_breakdown"][0]["stock_type"] == StockType.STOCKS.value
        assert result["holdings_value_breakdown"][0]["total_value"] == 3000.0


