import pytest

from model.order import Order, OrderStatus


def test_creates_reserved_order_by_default():
    order = Order(
        order_id="ORD-20260416-0043",
        sample_id="S-003",
        customer_name="삼성전자 파운드리",
        quantity=200,
        created_at="2026-04-16T09:32:15",
    )

    assert order.status == OrderStatus.RESERVED


@pytest.mark.parametrize(
    "field, value",
    [
        ("order_id", ""),
        ("sample_id", ""),
        ("customer_name", ""),
        ("quantity", 0),
        ("quantity", -1),
    ],
)
def test_rejects_invalid_fields(field, value):
    kwargs = dict(
        order_id="ORD-20260416-0043",
        sample_id="S-003",
        customer_name="고객",
        quantity=10,
        created_at="2026-04-16T09:32:15",
    )
    kwargs[field] = value

    with pytest.raises(ValueError):
        Order(**kwargs)


def test_to_dict_uses_schema_field_names():
    order = Order(
        order_id="ORD-20260416-0043",
        sample_id="S-003",
        customer_name="삼성전자 파운드리",
        quantity=200,
        created_at="2026-04-16T09:32:15",
    )

    assert order.to_dict() == {
        "orderId": "ORD-20260416-0043",
        "sampleId": "S-003",
        "customerName": "삼성전자 파운드리",
        "quantity": 200,
        "status": "RESERVED",
        "createdAt": "2026-04-16T09:32:15",
    }


def test_from_dict_round_trip():
    data = {
        "orderId": "ORD-20260416-0044",
        "sampleId": "S-004",
        "customerName": "고객사",
        "quantity": 5,
        "status": "CONFIRMED",
        "createdAt": "2026-04-16T10:00:00",
    }

    order = Order.from_dict(data)

    assert order.to_dict() == data


@pytest.mark.parametrize(
    "start, end",
    [
        (OrderStatus.RESERVED, OrderStatus.CONFIRMED),
        (OrderStatus.RESERVED, OrderStatus.PRODUCING),
        (OrderStatus.RESERVED, OrderStatus.REJECTED),
        (OrderStatus.PRODUCING, OrderStatus.CONFIRMED),
        (OrderStatus.CONFIRMED, OrderStatus.RELEASE),
    ],
)
def test_allows_valid_status_transitions(start, end):
    order = Order(
        order_id="ORD-20260416-0043",
        sample_id="S-003",
        customer_name="고객",
        quantity=1,
        created_at="2026-04-16T09:32:15",
        status=start,
    )

    order.transition_to(end)

    assert order.status == end


@pytest.mark.parametrize(
    "start, end",
    [
        (OrderStatus.RESERVED, OrderStatus.RELEASE),
        (OrderStatus.REJECTED, OrderStatus.CONFIRMED),
        (OrderStatus.RELEASE, OrderStatus.CONFIRMED),
        (OrderStatus.PRODUCING, OrderStatus.REJECTED),
    ],
)
def test_rejects_invalid_status_transitions(start, end):
    order = Order(
        order_id="ORD-20260416-0043",
        sample_id="S-003",
        customer_name="고객",
        quantity=1,
        created_at="2026-04-16T09:32:15",
        status=start,
    )

    with pytest.raises(ValueError):
        order.transition_to(end)
