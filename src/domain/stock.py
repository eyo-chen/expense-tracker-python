from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ActionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    TRANSFER = "TRANSFER"

@dataclass
class CreateStock:
    user_id: int
    symbol: str
    price: float
    quantity: int
    action_type: ActionType
    created_at: datetime

