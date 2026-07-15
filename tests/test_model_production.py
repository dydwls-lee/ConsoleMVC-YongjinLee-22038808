import pytest

from model.production import ProductionJob, ProductionQueue


def make_job(order_id="ORD-1", sample_id="S-001", shortage=10, yield_rate=0.3, avg_production_time=2.0):
    return ProductionJob.from_shortage(
        order_id=order_id,
        sample_id=sample_id,
        shortage=shortage,
        yield_rate=yield_rate,
        avg_production_time=avg_production_time,
    )


class TestProductionJob:
    def test_actual_quantity_is_ceil_of_shortage_over_yield(self):
        job = make_job(shortage=10, yield_rate=0.3)

        # ceil(10 / 0.3) = ceil(33.33..) = 34
        assert job.actual_quantity == 34

    def test_total_time_is_avg_time_times_actual_quantity(self):
        job = make_job(shortage=10, yield_rate=0.3, avg_production_time=2.0)

        assert job.total_time == pytest.approx(34 * 2.0)

    def test_exact_division_needs_no_extra_unit(self):
        job = make_job(shortage=9, yield_rate=0.3)

        # ceil(9 / 0.3) = ceil(30.0) = 30
        assert job.actual_quantity == 30


class TestProductionQueue:
    def test_fifo_ordering(self):
        queue = ProductionQueue()
        first = make_job(order_id="ORD-1")
        second = make_job(order_id="ORD-2")

        queue.enqueue(first)
        queue.enqueue(second)

        assert queue.current() is first
        assert queue.pending() == [second]

    def test_complete_current_removes_and_returns_job(self):
        queue = ProductionQueue()
        first = make_job(order_id="ORD-1")
        second = make_job(order_id="ORD-2")
        queue.enqueue(first)
        queue.enqueue(second)

        completed = queue.complete_current()

        assert completed is first
        assert queue.current() is second

    def test_current_is_none_when_empty(self):
        queue = ProductionQueue()

        assert queue.current() is None

    def test_complete_current_raises_when_empty(self):
        queue = ProductionQueue()

        with pytest.raises(ValueError):
            queue.complete_current()

    def test_len_reflects_total_waiting_jobs(self):
        queue = ProductionQueue()
        queue.enqueue(make_job(order_id="ORD-1"))
        queue.enqueue(make_job(order_id="ORD-2"))

        assert len(queue) == 2
