from typing import List
from abc import ABC, abstractmethod

from domain.stock import CreateStock, Stock
from domain.portfolio import PortfolioInfo


class AbstractStockUsecase(ABC):
    @abstractmethod
    def create(self, stock: CreateStock) -> str:
        """Create a new stock entry."""

    def list(self, user_id: int) -> List[Stock]:
        """List all stock by user id"""

    def get_portfolio_info(self, user_id: int) -> PortfolioInfo:
        """Get portfolio info"""
