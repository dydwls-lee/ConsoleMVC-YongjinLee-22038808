"""Production line domain model: job costing and FIFO scheduling queue.

Formulas are sourced from the root PRD "생산 계산 공식" section:
- 실 생산량 = ceil(부족분 / 수율)
- 총 생산 시간 = 평균 생산시간 * 실 생산량
- 스케줄링 전략: FIFO
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass


@dataclass
class ProductionJob:
    order_id: str
    sample_id: str
    actual_quantity: int
    total_time: float

    @classmethod
    def from_shortage(
        cls,
        order_id: str,
        sample_id: str,
        shortage: int,
        yield_rate: float,
        avg_production_time: float,
    ) -> "ProductionJob":
        actual_quantity = math.ceil(shortage / yield_rate)
        total_time = avg_production_time * actual_quantity
        return cls(
            order_id=order_id,
            sample_id=sample_id,
            actual_quantity=actual_quantity,
            total_time=total_time,
        )


class ProductionQueue:
    """FIFO queue for a single production line (one item at a time)."""

    def __init__(self) -> None:
        self._jobs: deque[ProductionJob] = deque()

    def enqueue(self, job: ProductionJob) -> None:
        self._jobs.append(job)

    def current(self) -> ProductionJob | None:
        return self._jobs[0] if self._jobs else None

    def pending(self) -> list[ProductionJob]:
        return list(self._jobs)[1:]

    def complete_current(self) -> ProductionJob:
        if not self._jobs:
            raise ValueError("no job is currently in production")
        return self._jobs.popleft()

    def __len__(self) -> int:
        return len(self._jobs)
