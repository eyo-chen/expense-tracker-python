from dataclasses import asdict, dataclass
from typing import TypedDict
from datetime import datetime
from utils.utils import custom_dict_factory
from .enum import ActionType, StockType


class CreateStockDict(TypedDict):
    user_id: int
    symbol: str
    price: float
    quantity: int
    action_type: str
    stock_type: str
    created_at: datetime


class StockDict(TypedDict):
    id: str
    user_id: int
    symbol: str
    price: float
    quantity: int
    action_type: str
    stock_type: str
    created_at: datetime
    updated_at: datetime


@dataclass
class StockInfo:
    symbol: str
    quantity: int
    price: float
    avg_cost: float
    percentage: float


@dataclass
class CreateStock:
    user_id: int
    symbol: str
    price: float
    quantity: int
    action_type: ActionType
    stock_type: StockType
    created_at: datetime

    def __post_init__(self):
        if not self.user_id or self.user_id <= 0:
            raise ValueError("user_id must be non-empty and greater than 0")
        if not self.symbol or self.symbol.strip() == "":
            raise ValueError("symbol must be a non-empty string")
        if self.price <= 0:
            raise ValueError("price must be greater than 0")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than 0")

    def as_dict(self) -> CreateStockDict:
        return asdict(self, dict_factory=custom_dict_factory)


@dataclass
class Stock:
    id: str
    user_id: int
    symbol: str
    price: float
    quantity: int
    action_type: ActionType
    stock_type: StockType
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not self.id:
            raise ValueError("id cannot be empty")
        if self.user_id <= 0:
            raise ValueError("user_id must be positive")
        if not self.symbol:
            raise ValueError("symbol cannot be empty")
        if self.price < 0:
            raise ValueError("price cannot be negative")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

    def as_dict(self) -> StockDict:
        return asdict(self, dict_factory=custom_dict_factory)
