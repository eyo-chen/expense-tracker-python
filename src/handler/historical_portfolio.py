import logging
from datetime import datetime, timezone
import grpc
from google.protobuf.empty_pb2 import Empty
import proto.historical_portfolio_pb2 as historical_portfolio_pb2
import proto.historical_portfolio_pb2_grpc as historical_portfolio_pb2_grpc
from usecase.base import AbstractHistoricalPortfolioUsecase
from domain.enum import DateOption


class HistoricalPortfolioService(historical_portfolio_pb2_grpc.HistoricalPortfolioService):
    def __init__(self, historical_portfolio_usecase: AbstractHistoricalPortfolioUsecase):
        self.historical_portfolio_usecase = historical_portfolio_usecase

    def Create(self, request, context):
        try:
            date = request.date.ToDatetime() if request.date else datetime.now(timezone.utc)
            self.historical_portfolio_usecase.create(user_id=request.user_id, date=date)
            return Empty()
        except Exception as e:
            logging.error(
                "Failed to create historical portfolio: %s",
                str(e),
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")
            raise grpc.RpcError("Internal server error")

    def GetPortfolioValue(self, request, context):
        try:
            date_option = DateOption(request.date_option)
            result = self.historical_portfolio_usecase.get_portfolio_value(
                user_id=request.user_id, 
                date_option=date_option
            )
            return historical_portfolio_pb2.GetPortfolioValueRes(
                date=result["date"],
                values=result["values"]
            )
        except ValueError as e:
            logging.error("Invalid date option: %s", str(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid date option")
            raise grpc.RpcError("Invalid date option")
        except Exception as e:
            logging.error(
                "Failed to get portfolio value: %s",
                str(e),
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")
            raise grpc.RpcError("Internal server error")
