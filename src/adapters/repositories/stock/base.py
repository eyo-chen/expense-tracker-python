from abc import ABC, abstractmethod
from domain.stock import CreateStock


class AbstractStockRepository(ABC):
    @abstractmethod
    def create(self, stock: CreateStock) -> str:
        """Create a new stock entry in the repository."""
        ...
