import pytest
from datetime import datetime
from unittest.mock import Mock
from usecase.stock.stock import StockUsecase
from domain.stock import CreateStock, ActionType


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
            created_at=datetime.utcnow(),
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
            created_at=datetime.utcnow(),
        )

        # Simulate an exception from the repository
        mock_repo.create.side_effect = Exception("Repository error")

        # Act/Assertion
        with pytest.raises(Exception, match="Repository error"):
            usecase.create(mock_stock)
        mock_repo.create.assert_called_once_with(mock_stock)
