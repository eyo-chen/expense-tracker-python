from domain.stock import CreateStock
from adapters.repositories.stock.base import AbstractStockRepository
from .base import AbstractStockUsecase


class StockUsecase(AbstractStockUsecase):
    def __init__(self, stock_repo: AbstractStockRepository):
        self.stock_repo = stock_repo

    def create(self, stock: CreateStock):
        return self.stock_repo.create(stock)
