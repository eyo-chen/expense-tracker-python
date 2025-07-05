import pytest
from datetime import datetime
from unittest.mock import Mock, ANY, patch
from usecase.historical_portfolio import HistoricalPortfolioUsecase
from domain.portfolio import Portfolio, Holding
from domain.enum import StockType
from domain.historical_portfolio import HistoricalPortfolio, HistoricalHolding


@pytest.fixture
def historical_portfolio_usecase():
    historical_portfolio_repo = Mock()
    portfolio_repo = Mock()
    usecase = HistoricalPortfolioUsecase(
        historical_portfolio_repo=historical_portfolio_repo, portfolio_repo=portfolio_repo
    )

    return usecase, historical_portfolio_repo, portfolio_repo


class TestHistoricalPortfolioUsecase:
    @patch.object(HistoricalPortfolioUsecase, "_get_stock_price")
    def test_get_portfolio_info_no_portfolio(self, mock_get_stock_price, historical_portfolio_usecase):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = historical_portfolio_usecase
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
    def test_get_portfolio_info_empty_portfolio(self, mock_get_stock_price, historical_portfolio_usecase):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = historical_portfolio_usecase
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
    def test_get_portfolio_info_no_valid_holdings(self, mock_get_stock_price, historical_portfolio_usecase):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = historical_portfolio_usecase
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
    def test_get_portfolio_info_with_valid_holdings(self, mock_get_stock_price, historical_portfolio_usecase):
        # Arrange
        usecase, historical_portfolio_repo, portfolio_repo = historical_portfolio_usecase
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
