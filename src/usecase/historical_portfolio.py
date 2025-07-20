from typing import List, Dict, Tuple, Callable, Any
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import yfinance as yf
from domain.enum import StockType, DateOption
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
        self._stock_price_cache: Dict[str, float] = {}

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

        # Calculate total stock value and holdings breakdown
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
        roi = round(((total_value - portfolio.total_money_in) / portfolio.total_money_in), 4) * 100

        current_datetime = datetime.now(timezone.utc)
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

    def get_portfolio_value(self, user_id: int, date_option: DateOption) -> Dict[str, List]:
        end_date = datetime.now(timezone.utc)
        start_date = _calculate_start_date(end_date, date_option)

        historical_portfolios = self.historical_portfolio_repo.get_by_user_and_date_range(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        if not historical_portfolios:
            return {"date": [], "values": []}

        # Group data based on date option requirements
        if date_option in {DateOption.THREE_MONTHS, DateOption.SIX_MONTHS, DateOption.NINE_MONTHS, DateOption.ONE_YEAR}:
            return _format_monthly_data(historical_portfolios, lambda p: p.portfolio_value)

        return _format_yearly_data(historical_portfolios, lambda p: p.portfolio_value)

    def get_gain(self, user_id: int, date_option: DateOption) -> Dict[str, List]:
        end_date = datetime.now(timezone.utc)
        start_date = _calculate_start_date(end_date, date_option)

        historical_portfolios = self.historical_portfolio_repo.get_by_user_and_date_range(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        if not historical_portfolios:
            return {"date": [], "values": []}

        # Group data based on date option requirements
        if date_option in {DateOption.THREE_MONTHS, DateOption.SIX_MONTHS, DateOption.NINE_MONTHS, DateOption.ONE_YEAR}:
            return _format_monthly_data(historical_portfolios, lambda p: p.gain)

        return _format_yearly_data(historical_portfolios, lambda p: p.gain)

    def get_stock_composition(self, user_id: int, date_option: DateOption) -> Dict[str, Any]:
        end_date = datetime.now(timezone.utc)
        start_date = _calculate_start_date(end_date, date_option)

        historical_portfolios = self.historical_portfolio_repo.get_by_user_and_date_range(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        if not historical_portfolios:
            return {"dates": [], "stocks": []}

        # Group data based on date option requirements
        if date_option in {DateOption.THREE_MONTHS, DateOption.SIX_MONTHS, DateOption.NINE_MONTHS, DateOption.ONE_YEAR}:
            return _format_stock_composition_monthly(historical_portfolios)

        return _format_stock_composition_yearly(historical_portfolios)

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


def _calculate_start_date(end_date: datetime, date_option: DateOption) -> datetime:
    if date_option == DateOption.THREE_MONTHS:
        return (end_date - relativedelta(months=3)).replace(day=1)
    elif date_option == DateOption.SIX_MONTHS:
        return (end_date - relativedelta(months=6)).replace(day=1)
    elif date_option == DateOption.NINE_MONTHS:
        return (end_date - relativedelta(months=9)).replace(day=1)
    elif date_option == DateOption.ONE_YEAR:
        return (end_date - relativedelta(years=1)).replace(day=1)
    elif date_option == DateOption.TWO_YEARS:
        return (end_date - relativedelta(years=2)).replace(day=1)
    elif date_option == DateOption.THREE_YEARS:
        return (end_date - relativedelta(years=3)).replace(day=1)
    else:  # ALL_TIME
        return datetime(2020, 1, 1, tzinfo=timezone.utc)


def _format_monthly_data(
    historical_portfolios: List[HistoricalPortfolio], value_selector: Callable[[HistoricalPortfolio], float]
) -> Dict[str, List]:
    dates = []
    values = []

    for portfolio in historical_portfolios:
        date_str = portfolio.date.strftime("%b %Y")
        dates.append(date_str)
        values.append(value_selector(portfolio))

    return {"date": dates, "values": values}


def _format_yearly_data(
    historical_portfolios: List[HistoricalPortfolio], value_selector: Callable[[HistoricalPortfolio], float]
) -> Dict[str, List]:
    total_months = len(historical_portfolios)

    if total_months <= 12:
        # Use all data points if 12 or fewer
        sampled_portfolios = historical_portfolios
    else:
        # Calculate interval to get ~12 points
        interval = max(1, total_months // 12)
        # Sample every Nth portfolio, limit to 12 points
        sampled_portfolios = historical_portfolios[::interval][:12]

    dates = [portfolio.date.strftime("%b %Y") for portfolio in sampled_portfolios]
    values = [value_selector(portfolio) for portfolio in sampled_portfolios]

    return {"date": dates, "values": values}


def _calculate_stock_composition_percentages(portfolios: List[HistoricalPortfolio]) -> Dict[str, Any]:
    """
    Calculate stock composition percentages over time for a list of portfolios.

    This function handles the core logic for converting portfolio holdings into percentage
    composition data suitable for time-series visualization.

    Key logic:
    1. First pass: Collect all unique stock symbols that appear in ANY portfolio period
    2. Second pass: For each portfolio period, calculate each stock's percentage of total holdings
    3. Ensure continuity: Stocks that don't appear in a period get 0.0% (e.g., when sold)

    Example:
    - Jan: AAPL=$900, MSFT=$900 (total=$1800) → AAPL=50%, MSFT=50%
    - Feb: AAPL=$1200, MSFT=$800 (total=$2000) → AAPL=60%, MSFT=40%
    - Mar: MSFT=$1100 (AAPL sold, total=$1100) → AAPL=0%, MSFT=100%

    Args:
        portfolios: List of HistoricalPortfolio objects to process

    Returns:
        Dict with format:
        {
            "dates": ["Jan 2024", "Feb 2024", "Mar 2024"],
            "stocks": [
                {"symbol": "AAPL", "percentages": [50.0, 60.0, 0.0]},
                {"symbol": "MSFT", "percentages": [50.0, 40.0, 100.0]}
            ]
        }
    """
    dates = []
    stock_percentages = {}

    # Step 1: First pass - collect all unique stock symbols that appear in any period
    # This ensures we track stocks even after they're sold (to show 0% in later periods)
    all_symbols = set()
    for portfolio in portfolios:
        for holding in portfolio.holdings_value_breakdown:
            all_symbols.add(holding.symbol)

    # Step 2: Initialize tracking for all symbols
    for symbol in all_symbols:
        stock_percentages[symbol] = []

    # Step 3: Second pass - calculate percentages for each period
    for portfolio in portfolios:
        date_str = portfolio.date.strftime("%b %Y")
        dates.append(date_str)

        # Calculate percentage for each stock present in this period
        current_period_percentages = {}
        if portfolio.holdings_value > 0:
            for holding in portfolio.holdings_value_breakdown:
                percentage = round((holding.total_value / portfolio.holdings_value) * 100, 1)
                current_period_percentages[holding.symbol] = percentage

        # Step 4: Add percentages for ALL symbols (0.0 if not present this period)
        # This is crucial for maintaining data consistency across time periods
        for symbol in all_symbols:
            percentage = current_period_percentages.get(symbol, 0.0)
            stock_percentages[symbol].append(percentage)

    # Step 5: Format into the required structure for API response
    stocks = []
    for symbol, percentages in stock_percentages.items():
        stocks.append({"symbol": symbol, "percentages": percentages})

    return {"dates": dates, "stocks": stocks}


def _format_stock_composition_monthly(historical_portfolios: List[HistoricalPortfolio]) -> Dict[str, Any]:
    return _calculate_stock_composition_percentages(historical_portfolios)


def _format_stock_composition_yearly(historical_portfolios: List[HistoricalPortfolio]) -> Dict[str, Any]:
    total_months = len(historical_portfolios)

    # Sample data for longer time periods to limit to ~12 data points
    if total_months <= 12:
        sampled_portfolios = historical_portfolios
    else:
        interval = max(1, total_months // 12)
        sampled_portfolios = historical_portfolios[::interval][:12]

    return _calculate_stock_composition_percentages(sampled_portfolios)
