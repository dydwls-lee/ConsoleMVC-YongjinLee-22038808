"""Controller for the '시료 주문' (place order) menu.

Validates sample id / customer name / quantity, then requests creation
of a RESERVED order. No console I/O happens here.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from model.order import Order
from model.repository import OrderRepository, SampleRepository

_ORDER_ID_FORMAT = "ORD-{date}-{seq:04d}"


class OrderController:
    def __init__(
        self,
        order_repository: OrderRepository,
        sample_repository: SampleRepository,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._orders = order_repository
        self._samples = sample_repository
        self._clock = clock

    def place_order(self, sample_id: str, customer_name: str, quantity: int) -> dict:
        if self._samples.get(sample_id) is None:
            raise ValueError(f"unknown sample id: {sample_id}")

        now = self._clock()
        order = Order(
            order_id=self._generate_order_id(now),
            sample_id=sample_id,
            customer_name=customer_name,
            quantity=quantity,
            created_at=now.strftime("%Y-%m-%dT%H:%M:%S"),
        )
        self._orders.add(order)
        return order.to_dict()

    def _generate_order_id(self, now: datetime) -> str:
        date_part = now.strftime("%Y%m%d")
        prefix = f"ORD-{date_part}-"
        seq = sum(1 for o in self._orders.list() if o.order_id.startswith(prefix)) + 1
        return _ORDER_ID_FORMAT.format(date=date_part, seq=seq)
