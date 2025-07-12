from datetime import datetime, timezone
from typing import List
from pymongo import MongoClient
from pymongo.database import Database
from .base import AbstractHistoricalPortfolioRepository
from domain.historical_portfolio import HistoricalPortfolio, HistoricalHolding
from domain.enum import StockType


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

    def get_by_user_and_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[HistoricalPortfolio]:
        query = {
            "user_id": user_id,
            "date": {
                "$gte": start_date.strftime("%Y-%m-%d"),
                "$lte": end_date.strftime("%Y-%m-%d")
            }
        }
        
        cursor = self.collection.find(query).sort("date", 1)
        
        historical_portfolios = []
        for doc in cursor:
            holdings = []
            for holding_dict in doc.get("holdings_value_breakdown", []):
                holding = HistoricalHolding(
                    symbol=holding_dict["symbol"],
                    shares=holding_dict["shares"],
                    stock_type=StockType(holding_dict["stock_type"]),
                    total_value=holding_dict["total_value"]
                )
                holdings.append(holding)
            
            date_obj = datetime.strptime(doc["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            created_at = doc["created_at"]
            updated_at = doc["updated_at"]
            
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            portfolio = HistoricalPortfolio(
                user_id=doc["user_id"],
                date=date_obj,
                portfolio_value=doc["portfolio_value"],
                cash_balance=doc["cash_balance"],
                money_in=doc["money_in"],
                holdings_value=doc["holdings_value"],
                holdings_value_breakdown=holdings,
                gain=doc["gain"],
                roi=doc["roi"],
                created_at=created_at,
                updated_at=updated_at
            )
            historical_portfolios.append(portfolio)
        
        return historical_portfolios

    def __del__(self):
        self.client.close()
