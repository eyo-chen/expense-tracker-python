from typing import List
from pymongo import MongoClient
from pymongo.database import Database
from .base import AbstractStockRepository
from domain.stock import CreateStock, Stock
from domain.enum import ActionType, StockType


class StockRepository(AbstractStockRepository):
    def __init__(self, mongo_client: MongoClient, database_name: str = "stock_db"):
        self.client = mongo_client
        self.db: Database = self.client[database_name]
        self.collection = self.db["stocks"]

    def create(self, stock: CreateStock) -> str:
        stock_dict = stock.as_dict()
        stock_dict["updated_at"] = stock_dict["created_at"]
        result = self.collection.insert_one(stock_dict)
        return str(result.inserted_id)

    def list(self, user_id: int) -> List[Stock]:
        stock_docs = self.collection.find({"user_id": user_id})

        stocks = [
            Stock(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                symbol=doc["symbol"],
                price=doc["price"],
                quantity=doc["quantity"],
                action_type=ActionType(doc["action_type"]),
                stock_type=StockType(doc["stock_type"]),
                date=doc["date"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
            for doc in stock_docs
        ]

        return stocks

    def __del__(self):
        self.client.close()
