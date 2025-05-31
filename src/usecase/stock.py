from typing import List

from domain.stock import CreateStock, Stock
from adapters.base import AbstractStockRepository
from .base import AbstractStockUsecase


class StockUsecase(AbstractStockUsecase):
    def __init__(self, stock_repo: AbstractStockRepository):
        self.stock_repo = stock_repo

    def create(self, stock: CreateStock):
        return self.stock_repo.create(stock)

    def list(self, user_id: int) -> List[Stock]:
        return self.stock_repo.list(user_id)
