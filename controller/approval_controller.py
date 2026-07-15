"""Controller for the '주문 승인/거절' (approve/reject) menu.

RESERVED 목록 조회, 승인 시 재고 확인 후 CONFIRMED/PRODUCING 자동 분기,
거절 시 REJECTED 처리를 담당한다. No console I/O happens here.
"""

from __future__ import annotations

from model.order import Order, OrderStatus
from model.production import ProductionJob, ProductionQueue
from model.repository import OrderRepository, SampleRepository


class ApprovalController:
    def __init__(
        self,
        order_repository: OrderRepository,
        sample_repository: SampleRepository,
        production_queue: ProductionQueue,
    ) -> None:
        self._orders = order_repository
        self._samples = sample_repository
        self._queue = production_queue

    def list_reserved(self) -> list[dict]:
        return [o.to_dict() for o in self._orders.list_by_status(OrderStatus.RESERVED)]

    def preview_approval(self, order_id: str) -> dict:
        """Report what `approve(order_id)` WOULD do, without mutating any
        state — so a caller can show the operator the shortage/production
        cost and ask for confirmation before actually committing to it.
        """
        order = self._get_reserved_order(order_id)
        sample = self._samples.get(order.sample_id)
        if sample is None:
            raise ValueError(f"unknown sample id: {order.sample_id}")

        if sample.stock >= order.quantity:
            return {"sufficient": True}

        shortage = order.quantity - sample.stock
        job = ProductionJob.from_shortage(
            order_id=order.order_id,
            sample_id=sample.id,
            shortage=shortage,
            yield_rate=sample.yield_rate,
            avg_production_time=sample.avg_production_time,
        )
        return {
            "sufficient": False,
            "shortage": shortage,
            "actualQuantity": job.actual_quantity,
            "totalTime": job.total_time,
        }

    def approve(self, order_id: str) -> dict:
        order = self._get_reserved_order(order_id)
        sample = self._samples.get(order.sample_id)
        if sample is None:
            raise ValueError(f"unknown sample id: {order.sample_id}")

        if sample.stock >= order.quantity:
            sample.stock -= order.quantity
            self._samples.update(sample)
            order.transition_to(OrderStatus.CONFIRMED)
            self._orders.update(order)
            return {"status": order.status.value, "order": order.to_dict()}

        shortage = order.quantity - sample.stock
        job = ProductionJob.from_shortage(
            order_id=order.order_id,
            sample_id=sample.id,
            shortage=shortage,
            yield_rate=sample.yield_rate,
            avg_production_time=sample.avg_production_time,
        )
        self._queue.enqueue(job)
        order.transition_to(OrderStatus.PRODUCING)
        self._orders.update(order)
        return {"status": order.status.value, "order": order.to_dict(), "job": job}

    def reject(self, order_id: str) -> dict:
        order = self._get_reserved_order(order_id)
        order.transition_to(OrderStatus.REJECTED)
        self._orders.update(order)
        return {"status": order.status.value, "order": order.to_dict()}

    def _get_reserved_order(self, order_id: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError(f"unknown order id: {order_id}")
        if order.status != OrderStatus.RESERVED:
            raise ValueError(
                f"order {order_id} is not RESERVED (current status: {order.status.value})"
            )
        return order
