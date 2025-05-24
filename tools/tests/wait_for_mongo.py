import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def wait_for_mongo(host="localhost", port=27017, timeout=30, db_name="test_stock_db"):
    """Wait for MongoDB to be ready by attempting to connect and ping."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            client = MongoClient(
                f"mongodb://{host}:{port}", serverSelectionTimeoutMS=1000
            )
            client.admin.command("ping")  # Ping the server to check if it's ready
            client.drop_database(db_name)  # Ensure clean state
            client.close()
            print("MongoDB is ready and test database cleared!")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError):
            print("MongoDB not ready, retrying...")
            time.sleep(1)
    raise TimeoutError("MongoDB did not become ready within the timeout period")


if __name__ == "__main__":
    wait_for_mongo()
