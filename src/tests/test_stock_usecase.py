import pytest
from unittest.mock import Mock, ANY, patch
from usecase.stock import StockUsecase
from domain.stock import CreateStock, Stock, StockInfo
from domain.portfolio import Portfolio, Holding, PortfolioInfo
from domain.enum import ActionType, StockType


@pytest.fixture
def stock_usecase():
    stock_repo = Mock()
    portfolio_repo = Mock()
    usecase = StockUsecase(stock_repo=stock_repo, portfolio_repo=portfolio_repo)
    return usecase, stock_repo, portfolio_repo


class TestStockUsecaseCreate:
    def test_create_transfer_new_portfolio(self, stock_usecase):
        # Arrange
        usecase, stock_repo, portfolio_repo = stock_usecase
        user_id, stock_id = 1, "123"
        stock = CreateStock(
            user_id=user_id,
            symbol="TRANSFER",
            price=3000.0,
            quantity=1,
            action_type=ActionType.TRANSFER,
            stock_type=StockType.STOCKS,
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
            symbol="TRANSFER",
            price=3000.0,
            quantity=1,
            action_type=ActionType.TRANSFER,
            stock_type=StockType.STOCKS,
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
            action_type=ActionType.BUY,
            stock_type=StockType.STOCKS,
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
            holdings=[Holding(symbol="TSLA", shares=2, stock_type=StockType.STOCKS, total_cost=4000.0)],
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
            action_type=ActionType.BUY,
            stock_type=StockType.STOCKS,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=5, stock_type=StockType.STOCKS, total_cost=750.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id
        updated_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=550.0,  # 1000 - (150 * 3)
            total_money_in=1000.0,
            holdings=[
                Holding(symbol="AAPL", shares=8, stock_type=StockType.STOCKS, total_cost=1200.0)
            ],  # 750 + (150 * 3)
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
            action_type=ActionType.SELL,
            stock_type=StockType.STOCKS,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=5, stock_type=StockType.STOCKS, total_cost=750.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = existing_portfolio
        stock_repo.create.return_value = stock_id
        updated_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1400.0,  # 1000 + (200 * 2)
            total_money_in=1000.0,
            holdings=[
                Holding(symbol="AAPL", shares=3, stock_type=StockType.STOCKS, total_cost=450.0)
            ],  # 750 - (150 * 2)
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
            action_type=ActionType.SELL,
            stock_type=StockType.STOCKS,
            created_at=ANY,
        )
        existing_portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=1000.0,
            holdings=[Holding(symbol="AAPL", shares=5, stock_type=StockType.STOCKS, total_cost=750.0)],
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
            action_type=ActionType.SELL,
            stock_type=StockType.STOCKS,
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
            action_type=ActionType.BUY,
            stock_type=StockType.STOCKS,
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
            action_type=ActionType.BUY,
            stock_type=StockType.STOCKS,
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
            action_type=ActionType.BUY,
            stock_type=StockType.STOCKS,
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


class TestStockUsecaseList:
    def test_list(self, stock_usecase):
        # Arrange
        usecase, mock_repo, _ = stock_usecase
        user_id = 1
        mock_stocks = [
            Stock(
                id="stock_123",
                user_id=1,
                symbol="AAPL",
                price=150.25,
                quantity=100,
                action_type=ActionType.BUY,
                stock_type=StockType.STOCKS,
                created_at=ANY,
                updated_at=ANY,
            ),
            Stock(
                id="stock_124",
                user_id=1,
                symbol="GOOGL",
                price=2800.50,
                quantity=10,
                action_type=ActionType.BUY,
                stock_type=StockType.STOCKS,
                created_at=ANY,
                updated_at=ANY,
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


class TestStockUsecaseGetStockPrice:
    @patch("usecase.stock.yf.Tickers")
    def test_get_stock_price_success_stocks(self, mock_yf_tickers, stock_usecase):
        # Arrange
        usecase, _, _ = stock_usecase
        stock_info = [("AAPL", StockType.STOCKS), ("GOOGL", StockType.STOCKS)]
        mock_ticker_aapl = Mock()
        mock_ticker_aapl.info = {"currentPrice": 150.0}
        mock_ticker_googl = Mock()
        mock_ticker_googl.info = {"currentPrice": 2800.0}
        mock_yf_tickers.return_value.tickers = {
            "AAPL": mock_ticker_aapl,
            "GOOGL": mock_ticker_googl,
        }

        # Act
        result = usecase._get_stock_price(stock_info=stock_info)

        # Assert
        mock_yf_tickers.assert_called_once_with(["AAPL", "GOOGL"])
        assert result == {"AAPL": 150.0, "GOOGL": 2800.0}

    @patch("usecase.stock.yf.Tickers")
    def test_get_stock_price_success_etf(self, mock_yf_tickers, stock_usecase):
        # Arrange
        usecase, _, _ = stock_usecase
        stock_info = [("SPY", StockType.ETF), ("VTI", StockType.ETF)]
        mock_ticker_spy = Mock()
        mock_ticker_spy.info = {"navPrice": 400.0}
        mock_ticker_vti = Mock()
        mock_ticker_vti.info = {"navPrice": 200.0}
        mock_yf_tickers.return_value.tickers = {
            "SPY": mock_ticker_spy,
            "VTI": mock_ticker_vti,
        }

        # Act
        result = usecase._get_stock_price(stock_info=stock_info)

        # Assert
        mock_yf_tickers.assert_called_once_with(["SPY", "VTI"])
        assert result == {"SPY": 400.0, "VTI": 200.0}

    @patch("usecase.stock.yf.Tickers")
    def test_get_stock_price_mixed_types(self, mock_yf_tickers, stock_usecase):
        # Arrange
        usecase, _, _ = stock_usecase
        stock_info = [("AAPL", StockType.STOCKS), ("SPY", StockType.ETF)]
        mock_ticker_aapl = Mock()
        mock_ticker_aapl.info = {"currentPrice": 150.0}
        mock_ticker_spy = Mock()
        mock_ticker_spy.info = {"navPrice": 400.0}
        mock_yf_tickers.return_value.tickers = {
            "AAPL": mock_ticker_aapl,
            "SPY": mock_ticker_spy,
        }

        # Act
        result = usecase._get_stock_price(stock_info=stock_info)

        # Assert
        mock_yf_tickers.assert_called_once_with(["AAPL", "SPY"])
        assert result == {"AAPL": 150.0, "SPY": 400.0}

    @patch("usecase.stock.yf.Tickers")
    def test_get_stock_price_empty_stock_info(self, mock_yf_tickers, stock_usecase):
        # Arrange
        usecase, _, _ = stock_usecase
        stock_info = []

        # Act
        result = usecase._get_stock_price(stock_info=stock_info)

        # Assert
        mock_yf_tickers.assert_not_called()
        assert result == {}

    @patch("usecase.stock.yf.Tickers")
    def test_get_stock_price_handles_api_error(self, mock_yf_tickers, stock_usecase):
        # Arrange
        usecase, _, _ = stock_usecase
        stock_info = [("AAPL", StockType.STOCKS), ("GOOGL", StockType.STOCKS)]
        mock_yf_tickers.side_effect = Exception("API error")

        # Act
        result = usecase._get_stock_price(stock_info=stock_info)

        # Assert
        mock_yf_tickers.assert_called_once_with(["AAPL", "GOOGL"])
        assert result == {"AAPL": 0.0, "GOOGL": 0.0}

    @patch("usecase.stock.yf.Tickers")
    def test_get_stock_price_missing_ticker(self, mock_yf_tickers, stock_usecase):
        # Arrange
        usecase, _, _ = stock_usecase
        stock_info = [("AAPL", StockType.STOCKS), ("INVALID", StockType.STOCKS)]
        mock_ticker_aapl = Mock()
        mock_ticker_aapl.info = {"currentPrice": 150.0}
        mock_yf_tickers.return_value.tickers = {"AAPL": mock_ticker_aapl}

        # Act
        result = usecase._get_stock_price(stock_info=stock_info)

        # Assert
        mock_yf_tickers.assert_called_once_with(["AAPL", "INVALID"])
        assert result == {"AAPL": 150.0, "INVALID": 0.0}

    @patch("usecase.stock.yf.Tickers")
    def test_get_stock_price_missing_price_field(self, mock_yf_tickers, stock_usecase):
        # Arrange
        usecase, _, _ = stock_usecase
        stock_info = [("AAPL", StockType.STOCKS), ("SPY", StockType.ETF)]
        mock_ticker_aapl = Mock()
        mock_ticker_aapl.info = {}  # No currentPrice
        mock_ticker_spy = Mock()
        mock_ticker_spy.info = {}  # No navPrice
        mock_yf_tickers.return_value.tickers = {
            "AAPL": mock_ticker_aapl,
            "SPY": mock_ticker_spy,
        }

        # Act
        result = usecase._get_stock_price(stock_info=stock_info)

        # Assert
        mock_yf_tickers.assert_called_once_with(["AAPL", "SPY"])
        assert result == {"AAPL": 0.0, "SPY": 0.0}


class TestStockUsecaseGetPortfolioInfo:
    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_portfolio_info_no_portfolio(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
        portfolio_repo.get.return_value = None
        expected_result = PortfolioInfo(user_id=user_id, total_portfolio_value=0.0, total_gain=0.0, roi=0.0)

        # Act
        result = usecase.get_portfolio_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        assert result == expected_result

    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_portfolio_info_empty_portfolio(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=0.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = portfolio
        expected_result = PortfolioInfo(user_id=user_id, total_portfolio_value=0.0, total_gain=0.0, roi=0.0)

        # Act
        result = usecase.get_portfolio_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        assert result == expected_result

    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_portfolio_info_no_valid_holdings(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=2000.0,
            holdings=[Holding(symbol="AAPL", shares=0, stock_type=StockType.STOCKS, total_cost=0.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = portfolio
        expected_result = PortfolioInfo(
            user_id=user_id,
            total_portfolio_value=1000.0,
            total_gain=-1000.0,
            roi=-50.0,
        )

        # Act
        result = usecase.get_portfolio_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        assert result == expected_result

    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_portfolio_info_with_valid_holdings(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
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
        expected_result = PortfolioInfo(
            user_id=user_id,
            total_portfolio_value=5000.0,
            total_gain=3000.0,
            roi=150,
        )

        # Act
        result = usecase.get_portfolio_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_called_once_with(stock_info=[("AAPL", StockType.STOCKS), ("SPY", StockType.ETF)])
        assert result == expected_result


class TestStockUsecaseGetStockInfo:
    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_stock_info_no_portfolio(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
        portfolio_repo.get.return_value = None
        expected_result = {StockType.ETF.value: [], StockType.STOCKS.value: [], "CASH": []}

        # Act
        result = usecase.get_stock_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        assert result == expected_result

    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_stock_info_empty_portfolio(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=0.0,
            total_money_in=0.0,
            holdings=[],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = portfolio
        expected_result = {StockType.ETF.value: [], StockType.STOCKS.value: [], "CASH": []}

        # Act
        result = usecase.get_stock_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        assert result == expected_result

    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_stock_info_no_valid_holdings(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=2000.0,
            holdings=[Holding(symbol="AAPL", shares=0, stock_type=StockType.STOCKS, total_cost=0.0)],
            created_at=ANY,
            updated_at=ANY,
        )
        portfolio_repo.get.return_value = portfolio
        expected_result = {StockType.ETF.value: [], StockType.STOCKS.value: [], "CASH": []}

        # Act
        result = usecase.get_stock_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_not_called()
        assert result == expected_result

    @patch.object(StockUsecase, "_get_stock_price")
    def test_get_stock_info_with_valid_holdings(self, mock_get_stock_price, stock_usecase):
        # Arrange
        usecase, _, portfolio_repo = stock_usecase
        user_id = 1
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=1000.0,
            total_money_in=2000.0,
            holdings=[
                Holding(symbol="AAPL", shares=10, stock_type=StockType.STOCKS, total_cost=1500.0),
                Holding(symbol="TSLA", shares=20, stock_type=StockType.STOCKS, total_cost=2000.0),
                Holding(symbol="SPY", shares=30, stock_type=StockType.ETF, total_cost=3000.0),
                Holding(symbol="QQQ", shares=5, stock_type=StockType.ETF, total_cost=1000.0),
            ],
            created_at=ANY,
            updated_at=ANY,
        )

        mock_get_stock_price.return_value = {"AAPL": 200.0, "TSLA": 500.0, "SPY": 400.0, "QQQ": 300.0}
        portfolio_repo.get.return_value = portfolio
        expected_result = {
            StockType.ETF.value: [
                StockInfo(
                    symbol="SPY",
                    quantity=30,
                    price=400.0,
                    avg_cost=100.0,  # 3000 / 30
                    percentage=45.0,  # 12000 / (1000 + 10*200 + 20*500 + 30*400 + 5*300)
                ),
                StockInfo(
                    symbol="QQQ",
                    quantity=5,
                    price=300.0,
                    avg_cost=200.0,  # 1000 / 5
                    percentage=6.0,  # 1500 / (1000 + 10*200 + 20*500 + 30*400 + 5*300)
                ),
            ],
            StockType.STOCKS.value: [
                StockInfo(
                    symbol="AAPL",
                    quantity=10,
                    price=200.0,
                    avg_cost=150.0,  # 1500 / 10
                    percentage=8.0,  # 2000 / (1000 + 10*200 + 20*500 + 30*400 + 5*300)
                ),
                StockInfo(
                    symbol="TSLA",
                    quantity=20,
                    price=500.0,
                    avg_cost=100.0,  # 2000 / 20
                    percentage=38.0,  # 10000 / (1000 + 10*200 + 20*500 + 30*400 + 5*300)
                ),
            ],
            "CASH": [
                StockInfo(
                    symbol="CASH",
                    quantity=1,
                    price=1000.0,
                    avg_cost=0.0,
                    percentage=4.0,  # 1000 / (1000 + 10*200 + 20*500 + 30*400 + 5*300)
                )
            ],
        }

        # Act
        result = usecase.get_stock_info(user_id)

        # Assert
        portfolio_repo.get.assert_called_once_with(user_id=user_id)
        mock_get_stock_price.assert_called_once_with(
            stock_info=[
                ("AAPL", StockType.STOCKS),
                ("TSLA", StockType.STOCKS),
                ("SPY", StockType.ETF),
                ("QQQ", StockType.ETF),
            ]
        )
        assert result == expected_result
