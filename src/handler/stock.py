from typing import List as ListType
import logging
from datetime import datetime, timezone
import grpc
import proto.stock_pb2 as stock_pb2
import proto.stock_pb2_grpc as stock_pb2_grpc
from usecase.base import AbstractStockUsecase
from domain.stock import CreateStock, Stock
from domain.enum import ActionType, ACTION_MAP, StockType, STOCK_MAP


class StockService(stock_pb2_grpc.StockService):
    def __init__(self, stock_usecase: AbstractStockUsecase):
        self.stock_usecase = stock_usecase

    def Create(self, request, context):
        try:
            stock = CreateStock(
                user_id=request.user_id,
                symbol=request.symbol,
                price=request.price,
                quantity=request.quantity,
                action_type=self._map_action_type(request.action),
                stock_type=self._map_stock_type(request.stock_type),
                created_at=datetime.now(timezone.utc),
            )

            stock_id = self.stock_usecase.create(stock)
            return stock_pb2.CreateResp(id=stock_id)
        except ValueError as e:
            logging.error("Invalid input for stock creation: %s", str(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid input: {str(e)}")
            raise grpc.RpcError(f"Invalid input: {str(e)}")
        except Exception as e:
            logging.error(
                "Failed to create stock for user_id=%s, symbol=%s: %s",
                request.user_id,
                request.symbol,
                str(e),
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")
            raise grpc.RpcError("Internal server error")

    def List(self, request, context):
        try:
            user_id = request.user_id
            stock_list = self.stock_usecase.list(user_id)

            return stock_pb2.ListResp(stock_list=self._convert_to_proto_stock_list(stock_list))
        except Exception as e:
            logging.error(
                "Failed to list stocks for user_id=%s: %s",
                request.user_id,
                str(e),
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")
            raise grpc.RpcError("Internal server error")

    def GetPortfolioInfo(self, request, context):
        try:
            user_id = request.user_id
            info = self.stock_usecase.get_portfolio_info(user_id=user_id)

            return stock_pb2.GetPortfolioInfoResp(
                user_id=user_id,
                total_portfolio_value=info.total_portfolio_value,
                total_gain=info.total_gain,
                roi=info.roi,
            )
        except Exception as e:
            logging.error(
                "Failed to get portfolio info for user_id=%s: %s",
                request.user_id,
                str(e),
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")
            raise grpc.RpcError("Internal server error")

    def _map_action_type(self, action: int) -> ActionType:
        if action not in ACTION_MAP:
            raise ValueError(f"Invalid action type: {action}. Must be 1 (BUY), 2 (SELL), or 3 (TRANSFER).")
        return ACTION_MAP[action]

    def _map_stock_type(self, stock_type: int) -> StockType:
        if stock_type not in STOCK_MAP:
            raise ValueError(f"Invalid stock type: {stock_type}. Must be 1 (STOCKS), 2 (ETF).")
        return STOCK_MAP[stock_type]

    def _convert_to_proto_stock_list(self, stock_list: ListType[Stock]):
        return [
            stock_pb2.Stock(
                id=stock.id,
                user_id=stock.user_id,
                symbol=stock.symbol,
                price=stock.price,
                quantity=stock.quantity,
                action=stock.action_type.value,
                stock_type=stock.stock_type.value,
                created_at=stock.created_at,
                updated_at=stock.updated_at,
            )
            for stock in stock_list
        ]
