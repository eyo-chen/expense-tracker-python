import pytest
from datetime import datetime, timezone
from unittest.mock import Mock
from usecase.stock import StockUsecase
from domain.stock import CreateStock, ActionType, Stock


@pytest.fixture
def stock_usecase():
    mock_repo = Mock()
    usecase = StockUsecase(stock_repo=mock_repo)
    return usecase, mock_repo


class TestStockUsecase:
    def test_create(self, stock_usecase):
        # Arrange
        usecase, mock_repo = stock_usecase
        mock_stock = CreateStock(
            user_id=1,
            symbol="AAPL",
            price=150.25,
            quantity=100,
            action_type=ActionType.BUY,
            created_at=datetime.now(timezone.utc),
        )

        # Define the expected return value from the mock repository
        expected_id = "stock_123"
        mock_repo.create.return_value = expected_id

        # Act
        result = usecase.create(mock_stock)

        # Assertion
        mock_repo.create.assert_called_once_with(mock_stock)
        assert result == expected_id

    def test_create_handles_repository_error(self, stock_usecase):
        # Arrange
        usecase, mock_repo = stock_usecase
        mock_stock = CreateStock(
            user_id=1,
            symbol="AAPL",
            price=150.25,
            quantity=100,
            action_type=ActionType.BUY,
            created_at=datetime.now(timezone.utc),
        )

        # Simulate an exception from the repository
        mock_repo.create.side_effect = Exception("Repository error")

        # Act/Assertion
        with pytest.raises(Exception, match="Repository error"):
            usecase.create(mock_stock)
        mock_repo.create.assert_called_once_with(mock_stock)

    def test_list(self, stock_usecase):
        # Arrange
        usecase, mock_repo = stock_usecase
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
        usecase, mock_repo = stock_usecase
        user_id = 1
        mock_repo.list.side_effect = Exception("Repository error")

        # Act/Assert
        with pytest.raises(Exception, match="Repository error"):
            usecase.list(user_id)
        mock_repo.list.assert_called_once_with(user_id)
