from typing import List, Dict
from datetime import datetime
from abc import ABC, abstractmethod
from domain.stock import CreateStock, Stock, StockInfo
from domain.portfolio import PortfolioInfo
from domain.enum import DateOption


class AbstractStockUsecase(ABC):
    @abstractmethod
    def create(self, stock: CreateStock) -> str:
        """Create a new stock entry."""

    @abstractmethod
    def list(self, user_id: int) -> List[Stock]:
        """List all stock by user id"""

    @abstractmethod
    def get_portfolio_info(self, user_id: int) -> PortfolioInfo:
        """Get portfolio info"""

    @abstractmethod
    def get_stock_info(self, user_id: int) -> Dict[str, List[StockInfo]]:
        """Get stock info by user id"""


class AbstractHistoricalPortfolioUsecase(ABC):
    @abstractmethod
    def create(self, user_id: int, date: datetime):
        """Create historical porfolio"""

    @abstractmethod
    def get_portfolio_value(self, user_id: int, date_option: DateOption) -> Dict[str, List]:
        """Get portfolio value over time based on date option"""
