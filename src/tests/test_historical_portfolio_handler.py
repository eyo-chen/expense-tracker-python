import pytest
import grpc
from handler.historical_portfolio import HistoricalPortfolioService
from unittest.mock import Mock
from usecase.base import AbstractHistoricalPortfolioUsecase


class TestHistoricalPortfolioCreate:
    @pytest.fixture
    def mock_historical_portfolio_usecase(self):
        usecase = Mock(spec=AbstractHistoricalPortfolioUsecase)
        return usecase

    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.set_code = Mock()
        context.set_details = Mock()
        return context

    @pytest.fixture
    def valid_request(self):
        request = Mock()
        request.user_id = 1
        request.date = None  # Use current date
        return request

    def test_success(self, mock_historical_portfolio_usecase, mock_context, valid_request):
        # Arrange
        service = HistoricalPortfolioService(mock_historical_portfolio_usecase)

        # Action
        service.Create(valid_request, mock_context)

        # Assertion
        mock_historical_portfolio_usecase.create.assert_called_once()
        mock_context.set_code.assert_not_called()
        mock_context.set_details.assert_not_called()

    def test_internal_error(self, mock_historical_portfolio_usecase, mock_context, valid_request):
        # Arrange
        service = HistoricalPortfolioService(mock_historical_portfolio_usecase)
        mock_historical_portfolio_usecase.create.side_effect = Exception("Server error")  # Simulate internal error

        # Act/Assertion
        with pytest.raises(grpc.RpcError) as exc_info:
            service.Create(valid_request, mock_context)
        assert str(exc_info.value) == "Internal server error"
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
        mock_context.set_details.assert_called_once_with("Internal server error")
        mock_historical_portfolio_usecase.create.assert_called_once()
