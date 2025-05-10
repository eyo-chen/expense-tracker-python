import grpc
from concurrent import futures
import proto.stock_pb2 as stock_pb2
import proto.stock_pb2_grpc as stock_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

class StockService(stock_pb2_grpc.StockService): 
  def Create(self, request, context): 
    return stock_pb2.CreateResp(id='123')

def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) 
  stock_pb2_grpc.add_StockServiceServicer_to_server(StockService(), server)
  server.add_insecure_port('[::]:50051') 
  server.start() 
  server.wait_for_termination()

if __name__ == '__main__':
  serve()