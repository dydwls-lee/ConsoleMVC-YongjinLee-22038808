"""Controller for the main menu summary header.

등록 시료 수 / 총 재고 / 전체 주문 수 / 생산라인 대기 건수를 집계한다.
No console I/O happens here.
"""

from __future__ import annotations

from model.production import ProductionQueue
from model.repository import OrderRepository, SampleRepository


class SummaryController:
    def __init__(
        self,
        sample_repository: SampleRepository,
        order_repository: OrderRepository,
        production_queue: ProductionQueue,
    ) -> None:
        self._samples = sample_repository
        self._orders = order_repository
        self._queue = production_queue

    def summarize(self) -> dict:
        samples = self._samples.list()
        return {
            "sampleCount": len(samples),
            "totalStock": sum(s.stock for s in samples),
            "totalOrderCount": len(self._orders.list()),
            "productionQueueLength": len(self._queue),
        }
