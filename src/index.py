import logging
import os
import grpc
import proto.stock_pb2_grpc as stock_pb2_grpc
import proto.historical_portfolio_pb2_grpc as historical_portfolio_pb2_grpc
from concurrent import futures
from pymongo import MongoClient
from dotenv import load_dotenv
from handler.stock import StockService
from handler.historical_portfolio import HistoricalPortfolioService
from adapters.stock import StockRepository
from adapters.historical_portfolio import HistoricalPortfolioRepository
from adapters.portfolio import PortfolioRepository
from usecase.stock import StockUsecase
from usecase.historical_portfolio import HistoricalPortfolioUsecase


load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def serve():
    logger.info("connecting to mongodb")
    client = MongoClient(os.getenv("MONGO_URI"))
    logger.info("connected to mongodb")

    stock_repo = StockRepository(client, "stock_db")
    portfolio_repo = PortfolioRepository(client, "stock_db")
    historical_portfolio_repo = HistoricalPortfolioRepository(client, "stock_db")
    historical_portfolio_usecase = HistoricalPortfolioUsecase(
        historical_portfolio_repo=historical_portfolio_repo, portfolio_repo=portfolio_repo
    )
    stock_usecase = StockUsecase(stock_repo, portfolio_repo)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stock_pb2_grpc.add_StockServiceServicer_to_server(StockService(stock_usecase), server)
    historical_portfolio_pb2_grpc.add_HistoricalPortfolioServiceServicer_to_server(
        HistoricalPortfolioService(historical_portfolio_usecase), server
    )
    server.add_insecure_port("[::]:50051")
    logger.info("server is running...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
