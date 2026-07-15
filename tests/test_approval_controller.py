import pytest

from controller.approval_controller import ApprovalController
from model.order import Order, OrderStatus
from model.production import ProductionQueue
from model.repository import InMemoryOrderRepository, InMemorySampleRepository
from model.sample import Sample


@pytest.fixture
def sample_repo():
    repo = InMemorySampleRepository()
    repo.add(Sample(id="S-001", name="웨이퍼", avg_production_time=2.0, yield_rate=0.3, stock=100))
    return repo


@pytest.fixture
def order_repo():
    return InMemoryOrderRepository()


@pytest.fixture
def production_queue():
    return ProductionQueue()


def add_reserved_order(order_repo, order_id="ORD-1", quantity=10):
    order = Order(
        order_id=order_id,
        sample_id="S-001",
        customer_name="고객",
        quantity=quantity,
        created_at="2026-04-16T09:00:00",
    )
    order_repo.add(order)
    return order


class TestListReserved:
    def test_returns_only_reserved_orders(self, sample_repo, order_repo, production_queue):
        add_reserved_order(order_repo, "ORD-1")
        confirmed = Order(
            order_id="ORD-2",
            sample_id="S-001",
            customer_name="고객",
            quantity=1,
            created_at="2026-04-16T09:00:00",
            status=OrderStatus.CONFIRMED,
        )
        order_repo.add(confirmed)
        controller = ApprovalController(order_repo, sample_repo, production_queue)

        result = controller.list_reserved()

        assert [o["orderId"] for o in result] == ["ORD-1"]


class TestApprove:
    def test_sufficient_stock_confirms_and_deducts_stock(self, sample_repo, order_repo, production_queue):
        add_reserved_order(order_repo, "ORD-1", quantity=10)
        controller = ApprovalController(order_repo, sample_repo, production_queue)

        result = controller.approve("ORD-1")

        assert result["status"] == "CONFIRMED"
        assert sample_repo.get("S-001").stock == 90
        assert order_repo.get("ORD-1").status == OrderStatus.CONFIRMED
        assert len(production_queue) == 0

    def test_insufficient_stock_moves_to_producing_and_enqueues_job(
        self, sample_repo, order_repo, production_queue
    ):
        add_reserved_order(order_repo, "ORD-1", quantity=150)
        controller = ApprovalController(order_repo, sample_repo, production_queue)

        result = controller.approve("ORD-1")

        assert result["status"] == "PRODUCING"
        assert order_repo.get("ORD-1").status == OrderStatus.PRODUCING
        assert len(production_queue) == 1
        job = production_queue.current()
        # shortage = 150 - 100 = 50, ceil(50/0.3) = 167
        assert job.actual_quantity == 167
        assert job.order_id == "ORD-1"

    def test_rejects_approving_non_reserved_order(self, sample_repo, order_repo, production_queue):
        order = add_reserved_order(order_repo, "ORD-1", quantity=10)
        order.transition_to(OrderStatus.REJECTED)
        order_repo.update(order)
        controller = ApprovalController(order_repo, sample_repo, production_queue)

        with pytest.raises(ValueError):
            controller.approve("ORD-1")

    def test_rejects_unknown_order(self, sample_repo, order_repo, production_queue):
        controller = ApprovalController(order_repo, sample_repo, production_queue)

        with pytest.raises(ValueError):
            controller.approve("ORD-missing")


class TestReject:
    def test_rejects_reserved_order(self, sample_repo, order_repo, production_queue):
        add_reserved_order(order_repo, "ORD-1")
        controller = ApprovalController(order_repo, sample_repo, production_queue)

        result = controller.reject("ORD-1")

        assert result["status"] == "REJECTED"
        assert order_repo.get("ORD-1").status == OrderStatus.REJECTED

    def test_rejects_rejecting_non_reserved_order(self, sample_repo, order_repo, production_queue):
        order = add_reserved_order(order_repo, "ORD-1")
        order.transition_to(OrderStatus.CONFIRMED)
        order_repo.update(order)
        controller = ApprovalController(order_repo, sample_repo, production_queue)

        with pytest.raises(ValueError):
            controller.reject("ORD-1")
