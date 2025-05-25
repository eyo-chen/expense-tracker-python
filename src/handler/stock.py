import logging
from datetime import datetime, timezone

import grpc
import proto.stock_pb2 as stock_pb2
import proto.stock_pb2_grpc as stock_pb2_grpc

from usecase.base import AbstractStockUsecase
from domain.stock import CreateStock, ActionType, ACTION_MAP


class StockService(stock_pb2_grpc.StockService):
    def __init__(self, stock_usecase: AbstractStockUsecase):
        self.stock_usecase = stock_usecase

    def Create(self, request, context):
        try:
            self._validate_create_request(request)
            stock = CreateStock(
                user_id=request.user_id,
                symbol=request.symbol,
                price=request.price,
                quantity=request.quantity,
                action_type=self._map_action_type(request.action),
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

    def _map_action_type(self, action: int) -> ActionType:
        if action not in ACTION_MAP:
            raise ValueError(f"Invalid action type: {action}. Must be 1 (BUY), 2 (SELL), or 3 (TRANSFER).")
        return ACTION_MAP[action]

    def _validate_create_request(self, request):
        if not request.user_id or request.user_id <= 0:
            raise ValueError("user_id must be non-empty and greater than 0")
        if not request.symbol or request.symbol.strip() == "":
            raise ValueError("symbol must be a non-empty string")
        if request.price <= 0:
            raise ValueError("price must be greater than 0")
        if request.quantity <= 0:
            raise ValueError("quantity must be greater than 0")
