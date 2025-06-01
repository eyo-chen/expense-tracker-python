from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Holding:
    symbol: str
    shares: int
    total_cost: float


@dataclass
class Portfolio:
    user_id: int
    cash_balance: float
    total_money_in: float
    holdings: List[Holding]
    created_at: datetime
    updated_at: datetime
