import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, ANY
from usecase.stock import StockUsecase
from domain.stock import CreateStock, ActionType, Stock
from domain.portfolio import Portfolio, Holding


@pytest.fixture
def stock_usecase():
    stock_repo = Mock()
    portfolio_repo = Mock()
    usecase = StockUsecase(stock_repo=stock_repo, portfolio_repo=portfolio_repo)
    return usecase, stock_repo, portfolio_repo


class TestStockUsecase:
    def test_create_transfer_new_portfolio(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "123"
        stock = CreateStock(
            user_id=user_id,
            symbol="",
            price=3000.0,
            quantity=1,
            action_type=ActionType.TRANSFER,
            created_at=ANY,
        )
        portfolio_repo.get.return_value = None
        stock_repo.create.return_value = stock_id
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=3000.0,
            total_money_in=3000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )

        # Act
        result = usecase.create(stock)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=portfolio)
        stock_repo.create.assert_called_once_with(stock)
        assert result == stock_id

    def test_create_transfer_existing_portfolio(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "123"
        stock = CreateStock(
            user_id=user_id,
            symbol="",
            price=3000.0,
            quantity=1,
            action_type=ActionType.TRANSFER,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=3000.0,
            total_money_in=3000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id
        updated_portfolio = Portfolio(
            user_id=existing_portfolio.user_id,
            cash_balance=6000.0,
            total_money_in=6000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )

        # Act
        result = usecase.create(stock)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=updated_portfolio)
        stock_repo.create.assert_called_once_with(stock)
        assert result == stock_id

    def test_create_buy_new_stock(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "123"
        stock = CreateStock(
            user_id=user_id,
            symbol="TSLA",
            price=2000.0,
            quantity=2,
            action_type=ActionType.BUY.value,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=5000.0,
            total_money_in=5000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id
        updated_portfolio = Portfolio(
            user_id=existing_portfolio.user_id,
            cash_balance=1000.0,
            total_money_in=5000.0,
            holdings=[Holding(symbol="TSLA", shares=2, total_cost=4000.0)],
            created_at=ANY,
            updated_at=ANY,
        )

        # Act
        result = usecase.create(stock)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=updated_portfolio)
        stock_repo.create.assert_called_once_with(stock)
        assert result == stock_id

    def test_create_buy_existing_holding(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "stock_126"
        stock = CreateStock(
            user_id=user_id,
            symbol="AAPL",
            price=150.0,
            quantity=3,
            action_type=ActionType.BUY.value,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=5, total_cost=750.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id
        updated_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=550.0,  # 1000 - (150 * 3)
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=8, total_cost=1200.0)],  # 750 + (150 * 3)
            created_at=ANY,
            updated_at=ANY,
        )

        # Act
        result = usecase.create(stock)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=updated_portfolio)
        stock_repo.create.assert_called_once_with(stock)
        assert result == stock_id

    def test_create_sell_existing_holding_partial(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "stock_127"
        stock = CreateStock(
            user_id=user_id,
            symbol="AAPL",
            price=200.0,
            quantity=2,
            action_type=ActionType.SELL.value,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=5, total_cost=750.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id
        updated_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1400.0,  # 1000 + (200 * 2)
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=3, total_cost=450.0)],  # 750 - (150 * 2)
            created_at=ANY,
            updated_at=ANY,
        )

        # Act
        result = usecase.create(stock)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=updated_portfolio)
        stock_repo.create.assert_called_once_with(stock)
        assert result == stock_id

    def test_create_sell_existing_holding_all_shares(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "stock_128"
        stock = CreateStock(
            user_id=user_id,
            symbol="AAPL",
            price=300.0,
            quantity=5,
            action_type=ActionType.SELL.value,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=5, total_cost=750.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id
        updated_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=2500.0,  # 1000 + (300 * 5)
            total_money_in=1000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )

        # Act
        result = usecase.create(stock)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=updated_portfolio)
        stock_repo.create.assert_called_once_with(stock)
        assert result == stock_id

    def test_create_sell_non_existent_holding(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "stock_129"
        stock = CreateStock(
            user_id=user_id,
            symbol="AAPL",
            price=150.0,
            quantity=5,
            action_type=ActionType.SELL.value,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id

        # Act/Assert
        with pytest.raises(Exception, match="Can not sell non-exist stock"):
            usecase.create(stock)
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_not_called()
        stock_repo.create.assert_not_called()

    def test_create_handles_repository_error_on_get(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "stock_130"
        stock = CreateStock(
            user_id=user_id,
            symbol="AAPL",
            price=150.0,
            quantity=10,
            action_type=ActionType.BUY.value,
            created_at=ANY,
        )
        portfolio_repo.get.side_effect = Exception("Portfolio repository error")
        stock_repo.create.return_value = stock_id

        # Act/Assert
        with pytest.raises(Exception, match="Portfolio repository error"):
            usecase.create(stock)
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_not_called()
        stock_repo.create.assert_not_called()

    def test_create_handles_repository_error_on_update(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "stock_131"
        stock = CreateStock(
            user_id=user_id,
            symbol="AAPL",
            price=150.0,
            quantity=10,
            action_type=ActionType.BUY.value,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=2000.0,
            total_money_in=2000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        portfolio_repo.update.side_effect = Exception("Portfolio update error")
        stock_repo.create.return_value = stock_id

        # Act/Assert
        with pytest.raises(Exception, match="Portfolio update error"):
            usecase.create(stock)
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=ANY)  # Portfolio may vary, so use ANY
        stock_repo.create.assert_not_called()

    def test_create_handles_repository_error_on_stock_create(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id = 1
        stock = CreateStock(
            user_id=user_id,
            symbol="AAPL",
            price=150.0,
            quantity=10,
            action_type=ActionType.BUY.value,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=2000.0,
            total_money_in=2000.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.side_effect = Exception("Stock create error")

        # Act/Assert
        with pytest.raises(Exception, match="Stock create error"):
            usecase.create(stock)
        portfolio_repo.get.assert_called_once_with(user_id)
        portfolio_repo.update.assert_called_once_with(portfolio=ANY)  # Portfolio may vary, so use ANY
        stock_repo.create.assert_called_once_with(stock)

    def test_list(self, stock_usecase):
        # Arrange
        usecase, mock_repo, _ = stock_usecase
        user_id = 1
        created_at = datetime.now(timezone.utc)
        mock_stocks = [
            Stock(
                id="stock_123",
                user_id=1,
                symbol="AAPL",
                price=150.25,
                quantity=100,
                action_type=ActionType.BUY,
                created_at=created_at,
                updated_at=created_at,
            ),
            Stock(
                id="stock_124",
                user_id=1,
                symbol="GOOGL",
                price=2800.50,
                quantity=10,
                action_type=ActionType.BUY,
                created_at=created_at,
                updated_at=created_at,
            ),
        ]
        mock_repo.list.return_value = mock_stocks

        # Act
        result = usecase.list(user_id)

        # Assert
        mock_repo.list.assert_called_once_with(user_id)
        assert result == mock_stocks
        assert len(result) == 2
        assert all(isinstance(stock, Stock) for stock in result)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "GOOGL"

    def test_list_handles_repository_error(self, stock_usecase):
        # Arrange
        usecase, mock_repo, _ = stock_usecase
        user_id = 1
        mock_repo.list.side_effect = Exception("Repository error")

        # Act/Assert
        with pytest.raises(Exception, match="Repository error"):
            usecase.list(user_id)
        mock_repo.list.assert_called_once_with(user_id)
