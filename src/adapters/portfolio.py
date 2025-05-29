from dataclasses import asdict
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.database import Database
from .base import AbstractPortfolioRepository
from domain.portfolio import Portfolio


class PortfolioRepository(AbstractPortfolioRepository):
    def __init__(self, mongo_client: MongoClient, database_name: str = "stock_db"):
        self.client = mongo_client
        self.db: Database = self.client[database_name]
        self.collection = self.db["portfolio"]

    def update(self, portfolio: Portfolio) -> None:
        portfolio.updated_at = datetime.now(timezone.utc)
        self.collection.replace_one({"user_id": portfolio.user_id}, asdict(portfolio), upsert=True)

    def __del__(self):
        self.client.close()
