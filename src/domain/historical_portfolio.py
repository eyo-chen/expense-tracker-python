from dataclasses import dataclass
from typing import List, TypedDict
from datetime import datetime
from dataclasses import asdict
from utils.utils import custom_dict_factory
from domain.enum import StockType

class HistoricalHoldingDict(TypedDict):
    symbol: str
    shares: int
    stock_type: str
    total_value: float


class HistoricalPortfolioDict(TypedDict):
    user_id: int
    date: datetime
    portfolio_value: float
    cash_balance: float
    cash_in: float
    holdings_value: float
    holdings_value_breakdown: List[HistoricalHoldingDict]
    gain: float
    roi: float
    created_at: datetime
    updated_at: datetime


@dataclass
class HistoricalHolding:
    symbol: str
    shares: int
    stock_type: StockType
    total_value: float

    def __post_init__(self):
        if not self.symbol:
            raise ValueError("symbol cannot be empty")
        if self.shares < 0:
            raise ValueError("shares cannot be negative")
        if self.total_value < 0:
            raise ValueError("total_value cannot be negative")

    def as_dict(self) -> HistoricalHoldingDict:
        return asdict(self, dict_factory=custom_dict_factory)


@dataclass
class HistoricalPortfolio:
    user_id: int
    date: datetime
    portfolio_value: float
    cash_balance: float
    cash_in: float
    holdings_value: float
    holdings_value_breakdown: List[HistoricalHolding]
    gain: float
    roi: float
    created_at: datetime
    updated_at: datetime

    def as_dict(self) -> HistoricalPortfolioDict:
        dict = asdict(self, dict_factory=custom_dict_factory)
        dict["date"] = self.date.strftime("%Y-%m-%d")
        return dict


