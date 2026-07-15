"""Controller for the "전체 주문 조회" option under the '시료 주문' menu.
Read-only.

Unlike the '모니터링' menu (MonitorController), which deliberately
excludes REJECTED from its status-count aggregate, this controller
exposes every order regardless of status, including REJECTED — it is
a plain history/audit view, not the aggregate monitoring rule.
No console I/O happens here.
"""

from __future__ import annotations

from model.repository import OrderRepository


class HistoryController:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._orders = order_repository

    def list_all(self) -> list[dict]:
        return [o.to_dict() for o in self._orders.list()]
