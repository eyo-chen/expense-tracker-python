from typing import List, Dict, Tuple
from datetime import datetime, timezone
import yfinance as yf
from .base import AbstractStockUsecase
from adapters.base import AbstractStockRepository, AbstractPortfolioRepository
from domain.portfolio import Portfolio, Holding, PortfolioInfo
from domain.stock import CreateStock, Stock, StockInfo
from domain.enum import ActionType, StockType

ETF_KEY = "navPrice"
STOCK_KEY = "currentPrice"


class StockUsecase(AbstractStockUsecase):
    def __init__(self, stock_repo: AbstractStockRepository, portfolio_repo: AbstractPortfolioRepository):
        self.stock_repo = stock_repo
        self.portfolio_repo = portfolio_repo
        self._stock_price_cache: Dict[str, float] = {}

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

            # Find the first holding
            holding = next((h for h in portfolio.holdings if h.symbol == symbol), None)
            if not holding:
                holding = Holding(symbol=symbol, shares=0, stock_type=stock.stock_type, total_cost=0.0)
                portfolio.holdings.append(holding)

            holding.shares += quantity
            holding.total_cost += price * quantity
        else:
            portfolio.cash_balance += price * quantity

            # Find the first holding
            holding = next((h for h in portfolio.holdings if h.symbol == symbol), None)
            if holding is None:
                raise Exception("Can not sell non-existent stock")

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

    def get_portfolio_info(self, user_id: int) -> PortfolioInfo:
        portfolio = self.portfolio_repo.get(user_id=user_id)
        if portfolio is None or portfolio.total_money_in == 0.0:
            return PortfolioInfo(user_id=user_id, total_portfolio_value=0.0, total_gain=0.0, roi=0.0)

        valid_holdings = [
            (holding.symbol, holding.shares, holding.stock_type) for holding in portfolio.holdings if holding.shares > 0
        ]
        if not valid_holdings:
            return PortfolioInfo(
                user_id=user_id,
                total_portfolio_value=portfolio.cash_balance,
                total_gain=portfolio.cash_balance - portfolio.total_money_in,
                # If no valid holdings, ROI depends only on cash balance
                roi=round((portfolio.cash_balance - portfolio.total_money_in) / portfolio.total_money_in, 4) * 100,
            )

        # Fetch prices in batch
        stock_info = [(symbol, stock_type) for symbol, _, stock_type in valid_holdings]
        stock_price_by_symbol = self._get_stock_price(stock_info=stock_info)

        # Calculate total stock value
        total_stock_price = sum(shares * stock_price_by_symbol.get(symbol, 0.0) for symbol, shares, _ in valid_holdings)

        # Compute ROI
        total_value = total_stock_price + portfolio.cash_balance
        roi = round((total_value - portfolio.total_money_in) / portfolio.total_money_in, 4) * 100

        return PortfolioInfo(
            user_id=user_id,
            total_portfolio_value=total_value,
            total_gain=total_value - portfolio.total_money_in,
            roi=roi,
        )

    def get_stock_info(self, user_id: int) -> Dict[str, List[StockInfo]]:
        result = {StockType.ETF.value: [], StockType.STOCKS.value: [], "CASH": []}
        portfolio = self.portfolio_repo.get(user_id=user_id)
        if portfolio is None or portfolio.total_money_in == 0.0:
            return result

        valid_holdings = [
            (holding.symbol, holding.shares, holding.stock_type, holding.total_cost)
            for holding in portfolio.holdings
            if holding.shares > 0
        ]
        if not valid_holdings:
            return result

        # Fetch prices in batch
        stock_info = [(symbol, stock_type) for symbol, _, stock_type, _ in valid_holdings]
        stock_price_by_symbol = self._get_stock_price(stock_info=stock_info)

        # Calculate total stock value and total value
        total_stock_price = sum(
            shares * stock_price_by_symbol.get(symbol, 0.0) for symbol, shares, _, _ in valid_holdings
        )
        total_value = total_stock_price + portfolio.cash_balance

        for symbol, shares, stock_type, total_cost in valid_holdings:
            stock_price = stock_price_by_symbol.get(symbol, 0.0)
            stock_total_value = shares * stock_price

            result[stock_type.value].append(
                StockInfo(
                    symbol=symbol,
                    quantity=shares,
                    price=stock_price,
                    avg_cost=round(total_cost / shares, 2),
                    percentage=round(stock_total_value / total_value, 4) * 100,
                )
            )

        result["CASH"].append(
            StockInfo(
                symbol="CASH",
                quantity=1,
                price=portfolio.cash_balance,
                avg_cost=0,
                percentage=round(portfolio.cash_balance / total_value, 4) * 100,
            )
        )

        # Sort ETF and STOCKS sections by percentage (descending order)
        result[StockType.ETF.value].sort(key=lambda x: x.percentage, reverse=True)
        result[StockType.STOCKS.value].sort(key=lambda x: x.percentage, reverse=True)

        return result

    def _get_stock_price(self, stock_info: List[Tuple[str, StockType]]) -> Dict[str, float]:
        if not stock_info:
            return {}

        # Fetch only symbols not in cache
        symbols = [symbol for symbol, _ in stock_info if symbol not in self._stock_price_cache]
        if not symbols:
            return self._stock_price_cache

        try:
            tickers = yf.Tickers(symbols)
            new_prices = {}

            for symbol, stock_type in stock_info:
                if symbol in self._stock_price_cache:
                    new_prices[symbol] = self._stock_price_cache[symbol]
                    continue

                ticker = tickers.tickers.get(symbol.upper())
                if ticker is None:
                    new_prices[symbol] = 0.0
                    continue

                price_field = STOCK_KEY if stock_type == StockType.STOCKS else ETF_KEY
                new_prices[symbol] = ticker.info.get(price_field, 0.0)

            # Update the cache with new prices
            self._stock_price_cache.update(new_prices)
            return self._stock_price_cache
        except Exception as e:
            print(f"Error fetching prices for symbols {[symbol for symbol, _ in stock_info]}: {e}")
            return {symbol: 0.0 for symbol, _ in stock_info}
