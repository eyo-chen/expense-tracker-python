from abc import ABC, abstractmethod

class AbstractCustomerRepository(ABC):
    @abstractmethod
    def create(self):
        ...