from typing import List, Dict
from abc import ABC, abstractmethod
from domain.stock import CreateStock, Stock, StockInfo
from domain.portfolio import PortfolioInfo


class AbstractStockUsecase(ABC):
    @abstractmethod
    def create(self, stock: CreateStock) -> str:
        """Create a new stock entry."""

    def list(self, user_id: int) -> List[Stock]:
        """List all stock by user id"""

    def get_portfolio_info(self, user_id: int) -> PortfolioInfo:
        """Get portfolio info"""

    def get_stock_info(self, user_id: int) -> Dict[str, List[StockInfo]]:
        """Get stock info by user id"""
