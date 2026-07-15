"""Controller for the '출고 처리' (release) menu.

CONFIRMED 주문 목록 조회, 선택 항목 RELEASE 전이를 담당한다.
No console I/O happens here.
"""

from __future__ import annotations

from model.order import OrderStatus
from model.repository import OrderRepository


class ReleaseController:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._orders = order_repository

    def list_confirmed(self) -> list[dict]:
        return [o.to_dict() for o in self._orders.list_by_status(OrderStatus.CONFIRMED)]

    def release(self, order_id: str) -> dict:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError(f"unknown order id: {order_id}")
        if order.status != OrderStatus.CONFIRMED:
            raise ValueError(
                f"order {order_id} is not CONFIRMED (current status: {order.status.value})"
            )
        order.transition_to(OrderStatus.RELEASE)
        self._orders.update(order)
        return order.to_dict()
