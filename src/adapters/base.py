from typing import List
from abc import ABC, abstractmethod

from domain.stock import CreateStock, Stock
from domain.portfolio import Portfolio


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
