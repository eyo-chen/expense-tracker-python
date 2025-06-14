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
