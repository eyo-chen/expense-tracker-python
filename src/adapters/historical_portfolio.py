from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.database import Database
from .base import AbstractHistoricalPortfolioRepository
from domain.historical_portfolio import HistoricalPortfolio


class HistoricalPortfolioRepository(AbstractHistoricalPortfolioRepository):
    def __init__(self, mongo_client: MongoClient, database_name: str = "stock_db"):
        self.client = mongo_client
        self.db: Database = self.client[database_name]
        self.collection = self.db["historical_portfolio"]

    def update(self, historical_portfolio: HistoricalPortfolio) -> None:
        historical_portfolio.updated_at = datetime.now(timezone.utc)
        self.collection.replace_one(
            {
                "user_id": historical_portfolio.user_id,
                "date": historical_portfolio.date.strftime("%Y-%m-%d"),
            },
            historical_portfolio.as_dict(),
            upsert=True,
        )

    def __del__(self):
        self.client.close()
