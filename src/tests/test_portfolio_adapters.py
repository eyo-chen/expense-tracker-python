import pytest
from datetime import datetime, timezone
from unittest.mock import ANY
from dataclasses import asdict
from pymongo import MongoClient
from domain.portfolio import Portfolio, Holding
from adapters.portfolio import PortfolioRepository


@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient("mongodb://localhost:27015")
    yield client
    client.drop_database("test_stock_db")
    client.close()


@pytest.fixture(scope="module")
def portfolio_repository(mongo_client):
    return PortfolioRepository(mongo_client, database_name="test_stock_db")


@pytest.fixture(scope="function", autouse=True)
def clear_collection(portfolio_repository):
    portfolio_repository.collection.delete_many({})


class TestPortfolioRepository:
    def test_update_new_portfolio(self, portfolio_repository):
        # Arrange
        created_at = datetime.now(timezone.utc)
        portfolio = Portfolio(
            user_id=1,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=10, total_cost=1500.0)],
            created_at=created_at,
            updated_at=created_at,
        )

        # Action
        portfolio_repository.update(portfolio)

        # Assertion
        result = portfolio_repository.collection.find_one({"user_id": 1})
        assert result["user_id"] == portfolio.user_id
        assert result["cash_balance"] == portfolio.cash_balance
        assert result["total_money_in"] == portfolio.total_money_in
        assert len(result["holdings"]) == 1
        assert result["holdings"][0]["symbol"] == "AAPL"
        assert result["holdings"][0]["shares"] == 10
        assert result["holdings"][0]["total_cost"] == 1500.0

    def test_update_existing_portfolio(self, portfolio_repository):
        # Arrange
        initial_portfolio = Portfolio(
            user_id=1,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=10, total_cost=1500.0)],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        portfolio_repository.collection.insert_one(asdict(initial_portfolio))

        updated_portfolio = Portfolio(
            user_id=1,
            cash_balance=2000.0,
            total_money_in=2000.0,
            holdings=[Holding(symbol="AAPL", shares=20, total_cost=3000.0)],
            created_at=initial_portfolio.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        # Action
        portfolio_repository.update(updated_portfolio)

        # Assertion
        result = portfolio_repository.collection.find_one({"user_id": 1})
        assert result is not None
        assert result["user_id"] == updated_portfolio.user_id
        assert result["cash_balance"] == 2000.0
        assert result["total_money_in"] == 2000.0
        assert len(result["holdings"]) == 1
        assert result["holdings"][0]["symbol"] == "AAPL"
        assert result["holdings"][0]["shares"] == 20
        assert result["holdings"][0]["total_cost"] == 3000.0

    def test_get_existing_portfolio(self, portfolio_repository):
        # Arrange
        created_at = datetime.now(timezone.utc)
        portfolio = Portfolio(
            user_id=1,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=10, total_cost=1500.0)],
            created_at=created_at,
            updated_at=created_at,
        )
        portfolio_repository.collection.insert_one(asdict(portfolio))
        expected_result = Portfolio(
            user_id=1,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=10, total_cost=1500.0)],
            created_at=ANY,
            updated_at=ANY,
        )

        # Action
        result = portfolio_repository.get(user_id=1)

        # Assertion
        assert result == expected_result

    def test_get_non_existent_portfolio(self, portfolio_repository):
        # Arrange
        created_at = datetime.now(timezone.utc)
        portfolio = Portfolio(
            user_id=1,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=10, total_cost=1500.0)],
            created_at=created_at,
            updated_at=created_at,
        )
        portfolio_repository.collection.insert_one(asdict(portfolio))

        # Action
        result = portfolio_repository.get(user_id=999)

        # Assertion
        assert result is None
