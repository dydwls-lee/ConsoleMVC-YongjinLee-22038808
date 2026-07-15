from controller.production_controller import ProductionController
from model.production import ProductionJob, ProductionQueue


def make_job(order_id):
    return ProductionJob.from_shortage(
        order_id=order_id, sample_id="S-001", shortage=10, yield_rate=0.5, avg_production_time=1.0
    )


def test_current_job_is_none_when_queue_empty():
    controller = ProductionController(ProductionQueue())

    assert controller.current_job() is None
    assert controller.pending_jobs() == []
    assert controller.queue_length() == 0


def test_reports_current_and_pending_jobs():
    queue = ProductionQueue()
    queue.enqueue(make_job("ORD-1"))
    queue.enqueue(make_job("ORD-2"))
    controller = ProductionController(queue)

    current = controller.current_job()
    pending = controller.pending_jobs()

    assert current["orderId"] == "ORD-1"
    assert [job["orderId"] for job in pending] == ["ORD-2"]
    assert controller.queue_length() == 2
