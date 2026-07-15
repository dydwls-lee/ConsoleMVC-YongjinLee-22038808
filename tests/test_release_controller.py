import pytest

from controller.release_controller import ReleaseController
from model.order import Order, OrderStatus
from model.repository import InMemoryOrderRepository


@pytest.fixture
def order_repo():
    return InMemoryOrderRepository()


def add_order(order_repo, order_id="ORD-1", status=OrderStatus.CONFIRMED):
    order = Order(
        order_id=order_id,
        sample_id="S-001",
        customer_name="고객",
        quantity=10,
        created_at="2026-04-16T09:00:00",
    )
    if status is not OrderStatus.RESERVED:
        order.transition_to(status)
    order_repo.add(order)
    return order


class TestListConfirmed:
    def test_returns_only_confirmed_orders(self, order_repo):
        add_order(order_repo, "ORD-1", OrderStatus.CONFIRMED)
        add_order(order_repo, "ORD-2", OrderStatus.RESERVED)
        controller = ReleaseController(order_repo)

        result = controller.list_confirmed()

        assert [o["orderId"] for o in result] == ["ORD-1"]


class TestRelease:
    def test_releases_confirmed_order(self, order_repo):
        add_order(order_repo, "ORD-1", OrderStatus.CONFIRMED)
        controller = ReleaseController(order_repo)

        result = controller.release("ORD-1")

        assert result["status"] == "RELEASE"
        assert order_repo.get("ORD-1").status == OrderStatus.RELEASE

    def test_rejects_releasing_non_confirmed_order(self, order_repo):
        add_order(order_repo, "ORD-1", OrderStatus.RESERVED)
        controller = ReleaseController(order_repo)

        with pytest.raises(ValueError):
            controller.release("ORD-1")

    def test_rejects_releasing_an_already_released_order(self, order_repo):
        add_order(order_repo, "ORD-1", OrderStatus.CONFIRMED)
        controller = ReleaseController(order_repo)
        controller.release("ORD-1")  # first release: CONFIRMED -> RELEASE

        with pytest.raises(ValueError):
            controller.release("ORD-1")

    def test_rejects_unknown_order(self, order_repo):
        controller = ReleaseController(order_repo)

        with pytest.raises(ValueError):
            controller.release("ORD-missing")
