from enum import Enum


class ActionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    TRANSFER = "TRANSFER"


ACTION_MAP = {
    1: ActionType.BUY,
    2: ActionType.SELL,
    3: ActionType.TRANSFER,
}


class StockType(Enum):
    STOCKS = "STOCKS"
    ETF = "ETF"


STOCK_MAP = {
    1: StockType.STOCKS,
    2: StockType.ETF,
}


class DateOption(Enum):
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    NINE_MONTHS = "9_months"
    ONE_YEAR = "1_year"
    TWO_YEARS = "2_years"
    THREE_YEARS = "3_years"
    ALL_TIME = "all_time"
