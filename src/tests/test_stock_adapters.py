import pytest
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from domain.stock import CreateStock, ActionType
from adapters.stock import StockRepository


@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient("mongodb://localhost:27017")
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
            created_at=datetime.utcnow(),
        )

        expected_result = {
            "user_id": mock_stock.user_id,
            "symbol": mock_stock.symbol,
            "price": mock_stock.price,
            "quantity": mock_stock.quantity,
            "action_type": mock_stock.action_type.value,
            "created_at": mock_stock.created_at,
            "updated_at": mock_stock.created_at,
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
        mock_stock1 = CreateStock(
            user_id=1,
            symbol="TSLA",
            price=110.25,
            quantity=50,
            action_type=ActionType.BUY,
            created_at=datetime.utcnow(),
        )
        mock_stock2 = CreateStock(
            user_id=1,
            symbol="GOOGL",
            price=2500.50,
            quantity=10,
            action_type=ActionType.SELL,
            created_at=datetime.utcnow(),
        )

        # Define expected results
        expected_result1 = {
            "user_id": mock_stock1.user_id,
            "symbol": mock_stock1.symbol,
            "price": mock_stock1.price,
            "quantity": mock_stock1.quantity,
            "action_type": mock_stock1.action_type.value,
            "created_at": mock_stock1.created_at,
            "updated_at": mock_stock1.created_at,
        }
        expected_result2 = {
            "user_id": mock_stock2.user_id,
            "symbol": mock_stock2.symbol,
            "price": mock_stock2.price,
            "quantity": mock_stock2.quantity,
            "action_type": mock_stock2.action_type.value,
            "created_at": mock_stock2.created_at,
            "updated_at": mock_stock2.created_at,
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
