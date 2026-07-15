import pytest

from controller.monitor_controller import MonitorController
from model.order import Order, OrderStatus
from model.repository import InMemoryOrderRepository, InMemorySampleRepository
from model.sample import Sample


@pytest.fixture
def sample_repo():
    repo = InMemorySampleRepository()
    repo.add(Sample(id="S-001", name="여유시료", avg_production_time=0.5, yield_rate=0.9, stock=100))
    repo.add(Sample(id="S-002", name="부족시료", avg_production_time=0.5, yield_rate=0.9, stock=5))
    repo.add(Sample(id="S-003", name="고갈시료", avg_production_time=0.5, yield_rate=0.9, stock=0))
    return repo


_TRANSITION_PATHS = {
    OrderStatus.RESERVED: [],
    OrderStatus.CONFIRMED: [OrderStatus.CONFIRMED],
    OrderStatus.PRODUCING: [OrderStatus.PRODUCING],
    OrderStatus.REJECTED: [OrderStatus.REJECTED],
    OrderStatus.RELEASE: [OrderStatus.CONFIRMED, OrderStatus.RELEASE],
}


@pytest.fixture
def order_repo():
    repo = InMemoryOrderRepository()
    orders = [
        ("ORD-1", "S-001", 10, OrderStatus.RESERVED),
        ("ORD-2", "S-002", 20, OrderStatus.CONFIRMED),
        ("ORD-3", "S-003", 5, OrderStatus.PRODUCING),
        ("ORD-4", "S-001", 999, OrderStatus.REJECTED),
        ("ORD-5", "S-001", 1, OrderStatus.RELEASE),
    ]
    for order_id, sample_id, qty, status in orders:
        order = Order(
            order_id=order_id,
            sample_id=sample_id,
            customer_name="고객",
            quantity=qty,
            created_at="2026-04-16T09:00:00",
        )
        for step in _TRANSITION_PATHS[status]:
            order.transition_to(step)
        repo.add(order)
    return repo


def test_status_counts_excludes_rejected(sample_repo, order_repo):
    controller = MonitorController(order_repo, sample_repo)

    counts = controller.status_counts()

    assert counts == {
        "RESERVED": 1,
        "PRODUCING": 1,
        "CONFIRMED": 1,
        "RELEASE": 1,
    }
    assert "REJECTED" not in counts


def test_stock_status_classifies_samples(sample_repo, order_repo):
    controller = MonitorController(order_repo, sample_repo)

    result = {row["id"]: row for row in controller.stock_status()}

    assert result["S-001"]["status"] == "여유"  # stock 100 >= demand 10
    assert result["S-002"]["status"] == "부족"  # stock 5 < demand 20
    assert result["S-003"]["status"] == "고갈"  # stock 0


def test_stock_status_treats_stock_exactly_equal_to_demand_as_sufficient():
    # Boundary: stock >= demand counts as "여유", not "부족", when they're
    # exactly equal.
    sample_repo = InMemorySampleRepository()
    sample_repo.add(Sample(id="S-010", name="딱맞는시료", avg_production_time=0.5, yield_rate=0.9, stock=10))
    order_repo = InMemoryOrderRepository()
    order_repo.add(
        Order(order_id="ORD-10", sample_id="S-010", customer_name="고객", quantity=10, created_at="2026-04-16T09:00:00")
    )
    controller = MonitorController(order_repo, sample_repo)

    result = {row["id"]: row for row in controller.stock_status()}

    assert result["S-010"]["status"] == "여유"


def test_stock_status_zero_stock_is_depleted_even_with_zero_demand():
    # Boundary: "고갈" is defined purely by stock == 0, regardless of
    # whether there's any outstanding demand at all.
    sample_repo = InMemorySampleRepository()
    sample_repo.add(Sample(id="S-011", name="무주문시료", avg_production_time=0.5, yield_rate=0.9, stock=0))
    order_repo = InMemoryOrderRepository()
    controller = MonitorController(order_repo, sample_repo)

    result = {row["id"]: row for row in controller.stock_status()}

    assert result["S-011"]["status"] == "고갈"
