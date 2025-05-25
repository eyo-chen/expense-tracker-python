from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ActionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    TRANSFER = "TRANSFER"


ACTION_MAP = {1: ActionType.BUY, 2: ActionType.SELL, 3: ActionType.TRANSFER}


@dataclass
class CreateStock:
    user_id: int
    symbol: str
    price: float
    quantity: int
    action_type: ActionType
    created_at: datetime
