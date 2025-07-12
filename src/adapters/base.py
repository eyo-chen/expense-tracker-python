from typing import List
from abc import ABC, abstractmethod
from datetime import datetime

from domain.stock import CreateStock, Stock
from domain.portfolio import Portfolio
from domain.historical_portfolio import HistoricalPortfolio


class AbstractStockRepository(ABC):
    @abstractmethod
    def create(self, stock: CreateStock) -> str:
        """Create a new stock entry in the repository."""

    @abstractmethod
    def list(self, user_id: int) -> List[Stock]:
        """List all stock by user id"""


class AbstractPortfolioRepository(ABC):
    @abstractmethod
    def update(self, portfolio: Portfolio) -> None:
        """Update portfolio in the repository"""

    @abstractmethod
    def get(self, user_id: int) -> Portfolio:
        """Get Portfolio"""


class AbstractHistoricalPortfolioRepository(ABC):
    @abstractmethod
    def update(self, portfolio: Portfolio) -> None:
        """Update or insert historical portfolio in the repository"""

    @abstractmethod
    def get_by_user_and_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[HistoricalPortfolio]:
        """Get historical portfolios for a user within a date range"""