import pytest

from model.order import Order, OrderStatus
from model.repository import InMemoryOrderRepository, InMemorySampleRepository
from model.sample import Sample


def make_sample(id="S-001", stock=10):
    return Sample(id=id, name="시료", avg_production_time=0.5, yield_rate=0.9, stock=stock)


def make_order(order_id="ORD-20260416-0001", sample_id="S-001", status=OrderStatus.RESERVED):
    return Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name="고객",
        quantity=1,
        created_at="2026-04-16T09:00:00",
        status=status,
    )


class TestInMemorySampleRepository:
    def test_add_and_get(self):
        repo = InMemorySampleRepository()
        sample = make_sample()

        repo.add(sample)

        assert repo.get("S-001") is sample

    def test_get_missing_returns_none(self):
        repo = InMemorySampleRepository()

        assert repo.get("S-999") is None

    def test_add_duplicate_id_raises(self):
        repo = InMemorySampleRepository()
        repo.add(make_sample())

        with pytest.raises(ValueError):
            repo.add(make_sample())

    def test_list_returns_all(self):
        repo = InMemorySampleRepository()
        repo.add(make_sample("S-001"))
        repo.add(make_sample("S-002"))

        assert {s.id for s in repo.list()} == {"S-001", "S-002"}

    def test_update_persists_changes(self):
        repo = InMemorySampleRepository()
        sample = make_sample(stock=10)
        repo.add(sample)

        sample.stock = 5
        repo.update(sample)

        assert repo.get("S-001").stock == 5

    def test_find_by_name_matches_substring(self):
        repo = InMemorySampleRepository()
        repo.add(Sample(id="S-001", name="실리콘 웨이퍼", avg_production_time=0.5, yield_rate=0.9, stock=1))
        repo.add(Sample(id="S-002", name="포토레지스트", avg_production_time=0.5, yield_rate=0.9, stock=1))

        result = repo.find_by_name("웨이퍼")

        assert [s.id for s in result] == ["S-001"]


class TestInMemoryOrderRepository:
    def test_add_and_get(self):
        repo = InMemoryOrderRepository()
        order = make_order()

        repo.add(order)

        assert repo.get("ORD-20260416-0001") is order

    def test_get_missing_returns_none(self):
        repo = InMemoryOrderRepository()

        assert repo.get("ORD-missing") is None

    def test_list_returns_all(self):
        repo = InMemoryOrderRepository()
        repo.add(make_order("ORD-1"))
        repo.add(make_order("ORD-2"))

        assert {o.order_id for o in repo.list()} == {"ORD-1", "ORD-2"}

    def test_list_by_status_filters(self):
        repo = InMemoryOrderRepository()
        repo.add(make_order("ORD-1", status=OrderStatus.RESERVED))
        repo.add(make_order("ORD-2", status=OrderStatus.CONFIRMED))

        reserved = repo.list_by_status(OrderStatus.RESERVED)

        assert [o.order_id for o in reserved] == ["ORD-1"]

    def test_update_persists_changes(self):
        repo = InMemoryOrderRepository()
        order = make_order()
        repo.add(order)

        order.transition_to(OrderStatus.REJECTED)
        repo.update(order)

        assert repo.get(order.order_id).status == OrderStatus.REJECTED
