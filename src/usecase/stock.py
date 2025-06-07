from typing import List
from datetime import datetime, timezone
from domain.stock import CreateStock, Stock, ActionType
from domain.portfolio import Portfolio, Holding
from adapters.base import AbstractStockRepository, AbstractPortfolioRepository
from .base import AbstractStockUsecase


class StockUsecase(AbstractStockUsecase):
    def __init__(self, stock_repo: AbstractStockRepository, portfolio_repo: AbstractPortfolioRepository):
        self.stock_repo = stock_repo
        self.portfolio_repo = portfolio_repo

    def create(self, stock: CreateStock) -> str:
        portfolio = self.portfolio_repo.get(stock.user_id)
        if portfolio is None:
            created_at = datetime.now(timezone.utc)
            portfolio = Portfolio(
                user_id=stock.user_id,
                cash_balance=0.0,
                total_money_in=0.0,
                holdings=[],
                created_at=created_at,
                updated_at=created_at,
            )

        symbol = stock.symbol
        price = stock.price
        quantity = stock.quantity
        action_type = ActionType(stock.action_type)

        if action_type == ActionType.TRANSFER:
            portfolio.cash_balance += price * quantity
            portfolio.total_money_in += price * quantity
        elif action_type == ActionType.BUY:
            portfolio.cash_balance -= price * quantity

            holding = next((h for h in portfolio.holdings if h.symbol == symbol), None)  # Find the first holding
            if not holding:
                holding = Holding(symbol=symbol, shares=0, total_cost=0.0)
                portfolio.holdings.append(holding)

            holding.shares += quantity
            holding.total_cost += price * quantity
        else:
            portfolio.cash_balance += price * quantity

            holding = next((h for h in portfolio.holdings if h.symbol == symbol), None)  # Find the first holding
            if holding is None:
                raise Exception("Can not sell non-exist stock")

            holding.shares -= quantity
            if holding.shares > 0:
                # Adjust total_cost proportionally (using average cost)
                avg_cost = holding.total_cost / (holding.shares + quantity)
                holding.total_cost -= avg_cost * quantity
            else:
                holding.total_cost = 0.0
                portfolio.holdings = [h for h in portfolio.holdings if h.shares > 0]

        self.portfolio_repo.update(portfolio=portfolio)
        return self.stock_repo.create(stock)

    def list(self, user_id: int) -> List[Stock]:
        return self.stock_repo.list(user_id)
