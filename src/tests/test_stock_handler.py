import pytest
import grpc
import proto.stock_pb2 as stock_pb2
from datetime import datetime, timezone
from unittest.mock import Mock
from handler.stock import StockService
from usecase.base import AbstractStockUsecase
from domain.stock import CreateStock, Stock
from domain.portfolio import PortfolioInfo
from domain.enum import ActionType, StockType


class TestStockServiceCreate:
    # Fixture to create a mock stock_usecase
    @pytest.fixture
    def mock_stock_usecase(self):
        usecase = Mock(spec=AbstractStockUsecase)
        usecase.create.return_value = "stock_123"  # Default successful return value
        return usecase

    # Fixture to create a mock gRPC context
    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.set_code = Mock()
        context.set_details = Mock()
        return context

    # Fixture to create a valid gRPC request
    @pytest.fixture
    def valid_request(self):
        request = Mock()
        request.user_id = 1
        request.symbol = "AAPL"
        request.price = 100.0
        request.quantity = 10
        request.action = 1  # Maps to ActionType.BUY
        request.stock_type = 1  # Maps to StockType.STOCKS
        return request

    def test_success(self, mock_stock_usecase, mock_context, valid_request):
        # Arrange
        service = StockService(mock_stock_usecase)

        # Action
        response = service.Create(valid_request, mock_context)

        # Assertion
        assert isinstance(response, stock_pb2.CreateResp)
        assert response.id == "stock_123"
        mock_stock_usecase.create.assert_called_once()
        args = mock_stock_usecase.create.call_args[0][0]  # Get the CreateStock object
        assert isinstance(args, CreateStock)
        assert args.user_id == 1
        assert args.symbol == "AAPL"
        assert args.price == 100.0
        assert args.quantity == 10
        assert args.action_type == ActionType.BUY
        assert isinstance(args.created_at, datetime)
        mock_context.set_code.assert_not_called()
        mock_context.set_details.assert_not_called()

    def test_invalid_user_id(self, mock_stock_usecase, mock_context):
        # Arrange
        service = StockService(mock_stock_usecase)
        request = Mock()
        request.user_id = 0  # Invalid
        request.symbol = "AAPL"
        request.price = 100.0
        request.quantity = 10
        request.action = 1
        request.stock_type = 1

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.Create(request, mock_context)
        assert str(exc_info.value) == "Invalid input: user_id must be non-empty and greater than 0"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_once_with("Invalid input: user_id must be non-empty and greater than 0")
        mock_stock_usecase.create.assert_not_called()

    def test_invalid_symbol(self, mock_stock_usecase, mock_context):
        # Arrange
        service = StockService(mock_stock_usecase)
        request = Mock()
        request.user_id = 1
        request.symbol = ""  # Invalid
        request.price = 100.0
        request.quantity = 10
        request.action = 1
        request.stock_type = 1

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.Create(request, mock_context)
        assert str(exc_info.value) == "Invalid input: symbol must be a non-empty string"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_once_with("Invalid input: symbol must be a non-empty string")
        mock_stock_usecase.create.assert_not_called()

    def test_invalid_price(self, mock_stock_usecase, mock_context):
        # Arrange
        service = StockService(mock_stock_usecase)
        request = Mock()
        request.user_id = 1
        request.symbol = "AAPL"
        request.price = 0.0  # Invalid
        request.quantity = 10
        request.action = 1
        request.stock_type = 1

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.Create(request, mock_context)
        assert str(exc_info.value) == "Invalid input: price must be greater than 0"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_once_with("Invalid input: price must be greater than 0")
        mock_stock_usecase.create.assert_not_called()

    def test_invalid_quantity(self, mock_stock_usecase, mock_context):
        # Arrange
        service = StockService(mock_stock_usecase)
        request = Mock()
        request.user_id = 1
        request.symbol = "AAPL"
        request.price = 100.0
        request.quantity = 0  # Invalid
        request.action = 1
        request.stock_type = 1

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.Create(request, mock_context)
        assert str(exc_info.value) == "Invalid input: quantity must be greater than 0"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_once_with("Invalid input: quantity must be greater than 0")
        mock_stock_usecase.create.assert_not_called()

    def test_invalid_action(self, mock_stock_usecase, mock_context):
        # Arrange
        service = StockService(mock_stock_usecase)
        request = Mock()
        request.user_id = 1
        request.symbol = "AAPL"
        request.price = 100.0
        request.quantity = 10
        request.action = 4  # Invalid
        request.stock_type = 1

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.Create(request, mock_context)
        assert (
            str(exc_info.value) == "Invalid input: Invalid action type: 4. Must be 1 (BUY), 2 (SELL), or 3 (TRANSFER)."
        )
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        mock_context.set_details.assert_called_once_with(
            "Invalid input: Invalid action type: 4. Must be 1 (BUY), 2 (SELL), or 3 (TRANSFER)."
        )
        mock_stock_usecase.create.assert_not_called()

    def test_internal_error(self, mock_stock_usecase, mock_context, valid_request):
        # Arrange
        service = StockService(mock_stock_usecase)
        mock_stock_usecase.create.side_effect = Exception("Database error")  # Simulate internal error

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.Create(valid_request, mock_context)
        assert str(exc_info.value) == "Internal server error"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
        mock_context.set_details.assert_called_once_with("Internal server error")
        mock_stock_usecase.create.assert_called_once()


class TestStockServiceList:
    # Fixture to create a mock stock_usecase
    @pytest.fixture
    def mock_stock_usecase(self):
        usecase = Mock(spec=AbstractStockUsecase)
        usecase.list.return_value = [
            Stock(
                id="stock_123",
                user_id=1,
                symbol="AAPL",
                price=100.0,
                quantity=10,
                action_type=ActionType.BUY,
                stock_type=StockType.STOCKS,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),  # Include if required
            ),
            Stock(
                id="stock_124",
                user_id=1,
                symbol="GOOGL",
                price=1500.0,
                quantity=5,
                action_type=ActionType.SELL,
                stock_type=StockType.STOCKS,
                created_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
                updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),  # Include if required
            ),
        ]
        return usecase

    # Fixture to create a mock gRPC context
    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.set_code = Mock()
        context.set_details = Mock()
        return context

    # Fixture to create a valid gRPC request
    @pytest.fixture
    def valid_request(self):
        request = Mock()
        request.user_id = 1
        return request

    def test_success(self, mock_stock_usecase, mock_context, valid_request):
        # Arrange
        service = StockService(mock_stock_usecase)

        # Action
        response = service.List(valid_request, mock_context)

        # Assertion
        assert isinstance(response, stock_pb2.ListResp)
        assert len(response.stock_list) == 2
        assert response.stock_list[0].id == "stock_123"
        assert response.stock_list[0].user_id == 1
        assert response.stock_list[0].symbol == "AAPL"
        assert response.stock_list[0].price == 100.0
        assert response.stock_list[0].quantity == 10
        assert response.stock_list[0].action == ActionType.BUY.value
        assert response.stock_list[0].stock_type == StockType.STOCKS.value
        assert response.stock_list[1].id == "stock_124"
        assert response.stock_list[1].user_id == 1
        assert response.stock_list[1].symbol == "GOOGL"
        assert response.stock_list[1].price == 1500.0
        assert response.stock_list[1].quantity == 5
        assert response.stock_list[1].action == ActionType.SELL.value
        assert response.stock_list[1].stock_type == StockType.STOCKS.value
        mock_stock_usecase.list.assert_called_once_with(1)
        mock_context.set_code.assert_not_called()
        mock_context.set_details.assert_not_called()

    def test_internal_error(self, mock_stock_usecase, mock_context, valid_request):
        # Arrange
        service = StockService(mock_stock_usecase)
        mock_stock_usecase.list.side_effect = Exception("Database error")  # Simulate internal error

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.List(valid_request, mock_context)
        assert str(exc_info.value) == "Internal server error"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
        mock_context.set_details.assert_called_once_with("Internal server error")
        mock_stock_usecase.list.assert_called_once_with(1)


class TestStockServiceGetPortfolioInfo:
    # Fixture to create a mock stock_usecase
    @pytest.fixture
    def mock_stock_usecase(self):
        usecase = Mock(spec=AbstractStockUsecase)
        usecase.get_portfolio_info.return_value = PortfolioInfo(
            user_id=1,
            total_portfolio_value=2500.0,
            total_gain=500.0,
            roi=25.0,
        )
        return usecase

    # Fixture to create a mock gRPC context
    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.set_code = Mock()
        context.set_details = Mock()
        return context

    # Fixture to create a valid gRPC request
    @pytest.fixture
    def valid_request(self):
        request = Mock()
        request.user_id = 1
        return request

    def test_success(self, mock_stock_usecase, mock_context, valid_request):
        # Arrange
        service = StockService(mock_stock_usecase)

        # Action
        response = service.get_portfolio_info(valid_request, mock_context)

        # Assertion
        assert isinstance(response, stock_pb2.GetPortfolioInfoResp)
        assert response.user_id == 1
        assert response.total_portfolio_value == 2500.0
        assert response.total_gain == 500.0
        assert response.roi == 25.0
        mock_stock_usecase.get_portfolio_info.assert_called_once_with(user_id=1)
        mock_context.set_code.assert_not_called()
        mock_context.set_details.assert_not_called()

    def test_internal_error(self, mock_stock_usecase, mock_context, valid_request):
        # Arrange
        service = StockService(mock_stock_usecase)
        mock_stock_usecase.get_portfolio_info.side_effect = Exception("Database error")  # Simulate internal error

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.get_portfolio_info(valid_request, mock_context)
        assert str(exc_info.value) == "Internal server error"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
        mock_context.set_details.assert_called_once_with("Internal server error")
        mock_stock_usecase.get_portfolio_info.assert_called_once_with(user_id=1)
