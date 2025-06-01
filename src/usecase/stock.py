from typing import List, Dict, Tuple
from datetime import datetime, timezone
import yfinance as yf
from .base import AbstractStockUsecase
from adapters.base import AbstractStockRepository, AbstractPortfolioRepository
from domain.portfolio import Portfolio, Holding
from domain.stock import CreateStock, Stock
from domain.enum import ActionType, StockType

ETF_KEY = "navPrice"
STOCK_KEY = "currentPrice"


class StockUsecase(AbstractStockUsecase):
    def __init__(self, stock_repo: AbstractStockRepository, portfolio_repo: AbstractPortfolioRepository):
        self.stock_repo = stock_repo
        self.portfolio_repo = portfolio_repo

    def create(self, stock: CreateStock) -> str:
        portfolio = self.portfolio_repo.get(stock.user_id)
        if portfolio is None:
            created_at = datetime.now(timezone.utc)
            portfolio = Portfolio(
                user_id=stock.user_id,
                cash_balance=0.0,
                total_money_in=0.0,
                holdings=[],
                created_at=created_at,
                updated_at=created_at,
            )

        symbol = stock.symbol
        price = stock.price
        quantity = stock.quantity
        action_type = stock.action_type

        if action_type == ActionType.TRANSFER:
            portfolio.cash_balance += price * quantity
            portfolio.total_money_in += price * quantity
        elif action_type == ActionType.BUY:
            portfolio.cash_balance -= price * quantity

            holding = next((h for h in portfolio.holdings if h.symbol == symbol), None)  # Find the first holding
            if not holding:
                holding = Holding(symbol=symbol, shares=0, stock_type=stock.stock_type, total_cost=0.0)
                portfolio.holdings.append(holding)

            holding.shares += quantity
            holding.total_cost += price * quantity
        else:
            portfolio.cash_balance += price * quantity

            holding = next((h for h in portfolio.holdings if h.symbol == symbol), None)  # Find the first holding
            if holding is None:
                raise Exception("Can not sell non-exist stock")

            holding.shares -= quantity
            if holding.shares > 0:
                # Adjust total_cost proportionally (using average cost)
                avg_cost = holding.total_cost / (holding.shares + quantity)
                holding.total_cost -= avg_cost * quantity
            else:
                holding.total_cost = 0.0
                portfolio.holdings = [h for h in portfolio.holdings if h.shares > 0]

        self.portfolio_repo.update(portfolio=portfolio)
        return self.stock_repo.create(stock)

    def list(self, user_id: int) -> List[Stock]:
        return self.stock_repo.list(user_id)

    def calculate_total_roi(self, user_id: int) -> float:
        portfolio = self.portfolio_repo.get(user_id=user_id)
        if portfolio is None or portfolio.total_money_in == 0.0:
            return 0.0

        valid_holdings = [
            (holding.symbol, holding.shares, holding.stock_type) for holding in portfolio.holdings if holding.shares > 0
        ]
        if not valid_holdings:
            # If no valid holdings, ROI depends only on cash balance
            return round(((portfolio.cash_balance - portfolio.total_money_in) / portfolio.total_money_in) * 100, 2)

        # Fetch prices in batch
        stock_info = [(symbol, stock_type) for symbol, _, stock_type in valid_holdings]
        stock_price_by_symbol = self._get_stock_price(stock_info=stock_info)

        # Calculate total stock value
        total_stock_price = sum(shares * stock_price_by_symbol.get(symbol, 0.0) for symbol, shares, _ in valid_holdings)

        # Compute ROI
        total_value = total_stock_price + portfolio.cash_balance
        roi = ((total_value - portfolio.total_money_in) / portfolio.total_money_in) * 100
        return round(roi, 2)

    def _get_stock_price(self, stock_info: List[Tuple[str, StockType]]) -> Dict[str, float]:
        if not stock_info:
            return {}

        try:
            symbols = [symbol for symbol, _ in stock_info]
            tickers = yf.Tickers(symbols)
            stock_price_by_symbol = {}

            for symbol, stock_type in stock_info:
                ticker = tickers.tickers.get(symbol.upper())
                if ticker is None:
                    stock_price_by_symbol[symbol] = 0.0
                    continue

                price_field = STOCK_KEY if stock_type == StockType.STOCKS else ETF_KEY
                stock_price_by_symbol[symbol] = ticker.info.get(price_field, 0.0)

            return stock_price_by_symbol
        except Exception as e:
            print(f"Error fetching prices for symbols {[symbol for symbol, _ in stock_info]}: {e}")
            return {symbol: 0.0 for symbol, _ in stock_info}
