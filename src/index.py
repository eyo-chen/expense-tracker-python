import logging
import os
import grpc
import proto.stock_pb2_grpc as stock_pb2_grpc
from concurrent import futures
from pymongo import MongoClient
from dotenv import load_dotenv
from handler.stock import StockService
from adapters.stock import StockRepository
from adapters.portfolio import PortfolioRepository
from usecase.stock import StockUsecase


load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



def serve():
    client = MongoClient(os.getenv("MONGO_URI"))
    logger.info("connected to mongodb")

    stock_repo = StockRepository(client, "stock_db")
    portfolio_repo = PortfolioRepository(client, "stock_db")
    stock_usecase = StockUsecase(stock_repo, portfolio_repo)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stock_pb2_grpc.add_StockServiceServicer_to_server(StockService(stock_usecase), server)
    server.add_insecure_port("[::]:50051")
    logger.info("server is running...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
