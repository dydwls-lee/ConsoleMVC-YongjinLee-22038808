import pytest

from controller.summary_controller import SummaryController
from model.order import Order
from model.production import ProductionJob, ProductionQueue
from model.repository import InMemoryOrderRepository, InMemorySampleRepository
from model.sample import Sample


def test_summarizes_counts_for_main_menu_header():
    sample_repo = InMemorySampleRepository()
    sample_repo.add(Sample(id="S-001", name="A", avg_production_time=0.5, yield_rate=0.9, stock=30))
    sample_repo.add(Sample(id="S-002", name="B", avg_production_time=0.5, yield_rate=0.9, stock=20))

    order_repo = InMemoryOrderRepository()
    order_repo.add(
        Order(
            order_id="ORD-1",
            sample_id="S-001",
            customer_name="고객",
            quantity=1,
            created_at="2026-04-16T09:00:00",
        )
    )

    queue = ProductionQueue()
    queue.enqueue(
        ProductionJob.from_shortage(
            order_id="ORD-1", sample_id="S-001", shortage=10, yield_rate=0.5, avg_production_time=1.0
        )
    )

    controller = SummaryController(sample_repo, order_repo, queue)

    summary = controller.summarize()

    assert summary == {
        "sampleCount": 2,
        "totalStock": 50,
        "totalOrderCount": 1,
        "productionQueueLength": 1,
    }
