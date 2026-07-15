from model.order import Order, OrderStatus
from model.repository import InMemoryOrderRepository

from controller.history_controller import HistoryController


def _order(order_id: str, status: OrderStatus) -> Order:
    return Order(
        order_id=order_id,
        sample_id="S-001",
        customer_name="고객사",
        quantity=1,
        created_at="2026-01-01T00:00:00",
        status=status,
    )


def test_list_all_includes_rejected_orders():
    repo = InMemoryOrderRepository()
    repo.add(_order("ORD-1", OrderStatus.RESERVED))
    repo.add(_order("ORD-2", OrderStatus.REJECTED))

    result = HistoryController(repo).list_all()

    assert {o["orderId"] for o in result} == {"ORD-1", "ORD-2"}
    assert {o["status"] for o in result} == {"RESERVED", "REJECTED"}
