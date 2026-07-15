"""Controller for the '생산 라인 조회' (production line) menu. Read-only.

Reports the job currently in production and the FIFO waiting queue.
No console I/O happens here.
"""

from __future__ import annotations

from model.production import ProductionJob, ProductionQueue


def _to_dict(job: ProductionJob) -> dict:
    return {
        "orderId": job.order_id,
        "sampleId": job.sample_id,
        "actualQuantity": job.actual_quantity,
        "totalTime": job.total_time,
    }


class ProductionController:
    def __init__(self, production_queue: ProductionQueue) -> None:
        self._queue = production_queue

    def current_job(self) -> dict | None:
        job = self._queue.current()
        return _to_dict(job) if job is not None else None

    def pending_jobs(self) -> list[dict]:
        return [_to_dict(job) for job in self._queue.pending()]

    def queue_length(self) -> int:
        return len(self._queue)
