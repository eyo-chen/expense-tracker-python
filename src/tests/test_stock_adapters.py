import pytest
from datetime import datetime, timezone
from pymongo import MongoClient
from unittest.mock import ANY
from bson.objectid import ObjectId
from adapters.stock import StockRepository
from domain.stock import CreateStock, Stock
from domain.enum import ActionType, StockType


@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient("mongodb://localhost:27015")
    yield client
    client.drop_database("test_stock_db")
    client.close()


@pytest.fixture(scope="module")
def stock_repository(mongo_client):
    return StockRepository(mongo_client, database_name="test_stock_db")


@pytest.fixture(scope="function", autouse=True)
def clear_collection(stock_repository):
    stock_repository.collection.delete_many({})


class TestStockRepository:
    def test_create_stock(self, stock_repository):
        mock_stock = CreateStock(
            user_id=1,
            symbol="AAPL",
            price=150.25,
            quantity=100,
            action_type=ActionType.BUY,
            stock_type=StockType.STOCKS,
            date=datetime(2025, 6, 29),
            created_at=datetime.now(timezone.utc),
        )

        expected_result = {
            "user_id": mock_stock.user_id,
            "symbol": mock_stock.symbol,
            "price": mock_stock.price,
            "quantity": mock_stock.quantity,
            "action_type": mock_stock.action_type.value,
            "stock_type": mock_stock.stock_type.value,
            "date": mock_stock.date,
        }

        stock_id = stock_repository.create(mock_stock)

        # Assertion
        stock_data = stock_repository.collection.find_one({"_id": ObjectId(stock_id)})
        fields_to_exclude = ["_id", "created_at", "updated_at"]
        stock_data_filtered = {k: v for k, v in stock_data.items() if k not in fields_to_exclude}
        expected_result_filtered = {k: v for k, v in expected_result.items() if k not in fields_to_exclude}

        assert stock_data_filtered == expected_result_filtered

    def test_create_multiple_stocks(self, stock_repository):
        # Create mock stocks
        created_at = datetime.now(timezone.utc)
        mock_stock1 = CreateStock(
            user_id=1,
            symbol="TSLA",
            price=110.25,
            quantity=50,
            action_type=ActionType.BUY,
            stock_type=StockType.STOCKS,
            created_at=created_at,
            date=datetime(2025, 6, 29),
        )
        mock_stock2 = CreateStock(
            user_id=1,
            symbol="GOOGL",
            price=2500.50,
            quantity=10,
            action_type=ActionType.SELL,
            stock_type=StockType.STOCKS,
            created_at=created_at,
            date=datetime(2025, 6, 29),
        )

        # Define expected results
        expected_result1 = {
            "user_id": mock_stock1.user_id,
            "symbol": mock_stock1.symbol,
            "price": mock_stock1.price,
            "quantity": mock_stock1.quantity,
            "action_type": mock_stock1.action_type.value,
            "stock_type": mock_stock1.stock_type.value,
            "date": mock_stock1.date,
        }
        expected_result2 = {
            "user_id": mock_stock2.user_id,
            "symbol": mock_stock2.symbol,
            "price": mock_stock2.price,
            "quantity": mock_stock2.quantity,
            "action_type": mock_stock2.action_type.value,
            "stock_type": mock_stock2.stock_type.value,
            "date": mock_stock2.date,
        }
        expected_data = [expected_result1, expected_result2]

        # Create stocks in the repository
        _ = stock_repository.create(mock_stock1)
        _ = stock_repository.create(mock_stock2)

        # Retrieve all stocks from MongoDB
        actual_data = list(stock_repository.collection.find({}))

        # Fields to exclude
        fields_to_exclude = {"_id", "created_at", "updated_at"}

        # Loop through each dictionary and exclude unwanted fields (a list of dictionaries)
        normalized_expected = [{k: v for k, v in item.items() if k not in fields_to_exclude} for item in expected_data]
        normalized_actual = [{k: v for k, v in item.items() if k not in fields_to_exclude} for item in actual_data]

        # Convert each dictionary to a tuple of sorted items and create sets
        expected_set = {tuple(item.items()) for item in normalized_expected}
        actual_set = {tuple(item.items()) for item in normalized_actual}

        # Compare the sets
        assert expected_set == actual_set, f"Expected {expected_set}, but got {actual_set}"

    def test_list_stocks(self, stock_repository):
        # Create mock stock data
        created_at = datetime.now(timezone.utc)
        mock_stock1 = {
            "user_id": 1,
            "symbol": "AAPL",
            "price": 150.25,
            "quantity": 100,
            "action_type": ActionType.BUY.value,
            "stock_type": StockType.STOCKS.value,
            "date": datetime(2025, 6, 29),
            "created_at": created_at,
            "updated_at": created_at,
        }
        mock_stock2 = {
            "user_id": 1,
            "symbol": "TSLA",
            "price": 110.25,
            "quantity": 50,
            "action_type": ActionType.SELL.value,
            "stock_type": StockType.STOCKS.value,
            "date": datetime(2025, 6, 29),
            "created_at": created_at,
            "updated_at": created_at,
        }
        mock_stock3 = {
            "user_id": 2,  # Different user_id
            "symbol": "GOOGL",
            "price": 2500.50,
            "quantity": 10,
            "action_type": ActionType.BUY.value,
            "stock_type": StockType.STOCKS.value,
            "date": datetime(2025, 6, 29),
            "created_at": created_at,
            "updated_at": created_at,
        }

        # Insert mock stocks directly into the MongoDB collection
        result1 = stock_repository.collection.insert_one(mock_stock1)
        result2 = stock_repository.collection.insert_one(mock_stock2)
        stock_repository.collection.insert_one(mock_stock3)

        # Get the inserted IDs
        stock_id1 = str(result1.inserted_id)
        stock_id2 = str(result2.inserted_id)

        # Expected Stock objects for user_id=1
        expected_stocks = [
            Stock(
                id=stock_id1,
                user_id=mock_stock1["user_id"],
                symbol=mock_stock1["symbol"],
                price=mock_stock1["price"],
                quantity=mock_stock1["quantity"],
                action_type=ActionType(mock_stock1["action_type"]),
                stock_type=StockType(mock_stock1["stock_type"]),
                date=datetime(2025, 6, 29),
                created_at=mock_stock1["created_at"],
                updated_at=mock_stock1["updated_at"],
            ),
            Stock(
                id=stock_id2,
                user_id=mock_stock2["user_id"],
                symbol=mock_stock2["symbol"],
                price=mock_stock2["price"],
                quantity=mock_stock2["quantity"],
                action_type=ActionType(mock_stock2["action_type"]),
                stock_type=StockType(mock_stock2["stock_type"]),
                date=datetime(2025, 6, 29),
                created_at=mock_stock2["created_at"],
                updated_at=mock_stock2["updated_at"],
            ),
        ]

        # Action
        result = stock_repository.list(1)

        # Assertions
        assert len(result) == 2, f"Expected 2 stocks, but got {len(result)}"
        assert all(isinstance(stock, Stock) for stock in result), "All results should be Stock objects"

        # Convert to sets for comparison (to ignore order)
        result_set = {
            (
                stock.id,
                stock.user_id,
                stock.symbol,
                stock.price,
                stock.quantity,
                stock.action_type,
                stock.stock_type,
            )
            for stock in result
        }
        expected_set = {
            (
                stock.id,
                stock.user_id,
                stock.symbol,
                stock.price,
                stock.quantity,
                stock.action_type,
                stock.stock_type,
            )
            for stock in expected_stocks
        }

        assert result_set == expected_set, f"Expected {expected_set}, but got {result_set}"

    def test_list_stocks_no_data(self, stock_repository):
        # Create mock stock data for user_id=1
        created_at = datetime.now(timezone.utc)
        mock_stock1 = {
            "user_id": 1,
            "symbol": "AAPL",
            "price": 150.25,
            "quantity": 100,
            "action_type": ActionType.BUY.value,
            "stock_type": StockType.STOCKS.value,
            "date": datetime(2025, 6, 29),
            "created_at": created_at,
            "updated_at": created_at,
        }
        mock_stock2 = {
            "user_id": 1,
            "symbol": "TSLA",
            "price": 110.25,
            "quantity": 50,
            "action_type": ActionType.SELL.value,
            "stock_type": StockType.STOCKS.value,
            "date": datetime(2025, 6, 29),
            "created_at": created_at,
            "updated_at": created_at,
        }

        # Insert mock stocks directly into the MongoDB collection
        stock_repository.collection.insert_many([mock_stock1, mock_stock2])

        # Query for a user_id with no stock data
        result = stock_repository.list(999)  # Non-existent user_id

        # Assertions
        assert len(result) == 0, f"Expected empty list, but got {len(result)} stocks"
        assert isinstance(result, list), "Result should be a list"
        assert all(isinstance(stock, Stock) for stock in result), "All results should be Stock objects (if any)"
