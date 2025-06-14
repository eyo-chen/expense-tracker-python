from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.database import Database
from .base import AbstractPortfolioRepository
from domain.portfolio import Portfolio, Holding
from domain.enum import StockType


class PortfolioRepository(AbstractPortfolioRepository):
    def __init__(self, mongo_client: MongoClient, database_name: str = "stock_db"):
        self.client = mongo_client
        self.db: Database = self.client[database_name]
        self.collection = self.db["portfolio"]

    def get(self, user_id: int) -> Portfolio:
        result = self.collection.find_one({"user_id": user_id})
        if result is None:
            return None

        return Portfolio(
            user_id=result["user_id"],
            cash_balance=result["cash_balance"],
            total_money_in=result["total_money_in"],
            holdings=[
                Holding(
                    symbol=holding["symbol"],
                    shares=holding["shares"],
                    stock_type=StockType(holding["stock_type"]),
                    total_cost=holding["total_cost"],
                )
                for holding in result["holdings"]
            ],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )

    def update(self, portfolio: Portfolio) -> None:
        portfolio.updated_at = datetime.now(timezone.utc)
        self.collection.replace_one({"user_id": portfolio.user_id}, portfolio.as_dict(), upsert=True)

    def __del__(self):
        self.client.close()
