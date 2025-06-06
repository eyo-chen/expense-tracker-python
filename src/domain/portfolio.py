from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, TypedDict
from .enum import StockType
from utils.utils import custom_dict_factory


class HoldingDict(TypedDict):
    symbol: str
    shares: int
    stock_type: str
    total_cost: float


class PortfolioDict(TypedDict):
    user_id: int
    cash_balance: float
    total_money_in: float
    holdings: List[HoldingDict]
    created_at: datetime
    updated_at: datetime


@dataclass
class Holding:
    symbol: str
    shares: int
    stock_type: StockType
    total_cost: float

    def __post_init__(self):
        if not self.symbol:
            raise ValueError("symbol cannot be empty")
        if self.shares < 0:
            raise ValueError("shares cannot be negative")
        if self.total_cost < 0:
            raise ValueError("total_cost cannot be negative")

    def as_dict(self) -> HoldingDict:
        return asdict(self, dict_factory=custom_dict_factory)


@dataclass
class Portfolio:
    user_id: int
    cash_balance: float
    total_money_in: float
    holdings: List[Holding]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if self.total_money_in < 0:
            raise ValueError("total_money_in cannot be negative")

    def as_dict(self) -> PortfolioDict:
        return asdict(self, dict_factory=custom_dict_factory)


@dataclass
class PortfolioInfo:
    user_id: int
    total_portfolio_value: float
    total_gain: float
    roi: float
