from datetime import datetime

import pytest

from controller.order_controller import OrderController
from model.repository import InMemoryOrderRepository, InMemorySampleRepository
from model.sample import Sample


@pytest.fixture
def sample_repo():
    repo = InMemorySampleRepository()
    repo.add(Sample(id="S-001", name="웨이퍼", avg_production_time=0.5, yield_rate=0.9, stock=100))
    return repo


@pytest.fixture
def order_repo():
    return InMemoryOrderRepository()


def make_controller(sample_repo, order_repo, now=datetime(2026, 4, 16, 9, 32, 15)):
    return OrderController(order_repo, sample_repo, clock=lambda: now)


class TestPlaceOrder:
    def test_creates_reserved_order_with_generated_id(self, sample_repo, order_repo):
        controller = make_controller(sample_repo, order_repo)

        result = controller.place_order(sample_id="S-001", customer_name="삼성전자", quantity=10)

        assert result["orderId"] == "ORD-20260416-0001"
        assert result["status"] == "RESERVED"
        assert result["createdAt"] == "2026-04-16T09:32:15"

    def test_second_order_same_day_increments_sequence(self, sample_repo, order_repo):
        controller = make_controller(sample_repo, order_repo)
        controller.place_order(sample_id="S-001", customer_name="삼성전자", quantity=10)

        second = controller.place_order(sample_id="S-001", customer_name="SK하이닉스", quantity=5)

        assert second["orderId"] == "ORD-20260416-0002"

    def test_rejects_unknown_sample_id(self, sample_repo, order_repo):
        controller = make_controller(sample_repo, order_repo)

        with pytest.raises(ValueError):
            controller.place_order(sample_id="S-999", customer_name="고객", quantity=1)

    def test_rejects_non_positive_quantity(self, sample_repo, order_repo):
        controller = make_controller(sample_repo, order_repo)

        with pytest.raises(ValueError):
            controller.place_order(sample_id="S-001", customer_name="고객", quantity=0)
