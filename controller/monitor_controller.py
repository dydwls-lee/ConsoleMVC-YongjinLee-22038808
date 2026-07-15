"""Controller for the '모니터링' (monitoring) menu. Read-only.

Aggregates order counts per status (REJECTED excluded per root PRD) and
classifies each sample's stock as 여유/부족/고갈 against outstanding
order demand. No console I/O happens here.
"""

from __future__ import annotations

from model.order import OrderStatus
from model.repository import OrderRepository, SampleRepository

_MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
]

# Outstanding demand = orders not yet shipped and not rejected.
_OUTSTANDING_STATUSES = {OrderStatus.RESERVED, OrderStatus.PRODUCING, OrderStatus.CONFIRMED}


class MonitorController:
    def __init__(self, order_repository: OrderRepository, sample_repository: SampleRepository) -> None:
        self._orders = order_repository
        self._samples = sample_repository

    def status_counts(self) -> dict:
        return {
            status.value: len(self._orders.list_by_status(status))
            for status in _MONITORED_STATUSES
        }

    def stock_status(self) -> list[dict]:
        demand_by_sample = self._outstanding_demand_by_sample()
        rows = []
        for sample in self._samples.list():
            demand = demand_by_sample.get(sample.id, 0)
            rows.append(
                {
                    "id": sample.id,
                    "name": sample.name,
                    "stock": sample.stock,
                    "demand": demand,
                    "status": self._classify(sample.stock, demand),
                }
            )
        return rows

    def _outstanding_demand_by_sample(self) -> dict:
        demand: dict = {}
        for status in _OUTSTANDING_STATUSES:
            for order in self._orders.list_by_status(status):
                demand[order.sample_id] = demand.get(order.sample_id, 0) + order.quantity
        return demand

    @staticmethod
    def _classify(stock: int, demand: int) -> str:
        if stock == 0:
            return "고갈"
        if stock < demand:
            return "부족"
        return "여유"
