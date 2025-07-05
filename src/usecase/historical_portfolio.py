from typing import List, Dict, Tuple
from datetime import datetime, timezone
import yfinance as yf
from domain.enum import StockType
from domain.historical_portfolio import HistoricalPortfolio, HistoricalHolding
from .base import AbstractHistoricalPortfolioUsecase
from adapters.base import AbstractHistoricalPortfolioRepository, AbstractPortfolioRepository

ETF_KEY = "navPrice"
STOCK_KEY = "currentPrice"


class HistoricalPortfolioUsecase(AbstractHistoricalPortfolioUsecase):
    def __init__(
        self,
        historical_portfolio_repo: AbstractHistoricalPortfolioRepository,
        portfolio_repo: AbstractPortfolioRepository,
    ):
        self.historical_portfolio_repo = historical_portfolio_repo
        self.portfolio_repo = portfolio_repo

    def create(self, user_id: int, date: datetime):
        start_date_of_month = date.replace(day=1)
        portfolio = self.portfolio_repo.get(user_id=user_id)
        if portfolio is None or portfolio.total_money_in == 0.0:
            return

        valid_holdings = [
            (holding.symbol, holding.shares, holding.stock_type) for holding in portfolio.holdings if holding.shares > 0
        ]
        if not valid_holdings:
            return

        # Fetch prices in batch
        stock_info = [(symbol, stock_type) for symbol, _, stock_type in valid_holdings]
        stock_price_by_symbol = self._get_stock_price(stock_info=stock_info)

        # Calculate total stock value
        total_stock_price = 0.0
        holdings_value_breakdown = []
        for symbol, shares, stock_type in valid_holdings:
            holding_total_value = shares * stock_price_by_symbol.get(symbol, 0.0)
            total_stock_price += holding_total_value

            holdings_value_breakdown.append(
                HistoricalHolding(
                    symbol=symbol,
                    shares=shares,
                    stock_type=stock_type,
                    total_value=holding_total_value,
                )
            )

        # Compute ROI
        total_value = total_stock_price + portfolio.cash_balance
        roi = round(((total_value - portfolio.total_money_in) / portfolio.total_money_in) * 100, 2)

        current_datetime = (datetime.now(timezone.utc),)
        historical_portfolio = HistoricalPortfolio(
            user_id=user_id,
            date=start_date_of_month,
            portfolio_value=total_value,
            cash_balance=portfolio.cash_balance,
            money_in=portfolio.total_money_in,
            holdings_value=total_stock_price,
            holdings_value_breakdown=holdings_value_breakdown,
            gain=total_value - portfolio.total_money_in,
            roi=roi,
            created_at=current_datetime,
            updated_at=current_datetime,
        )
        self.historical_portfolio_repo.update(historical_portfolio)

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
