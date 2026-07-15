"""Repository interfaces and in-memory stand-in implementations.

This PoC stage does not have access to the real `data-persistence`
module (developed in parallel, in a separate repo). Per this module's
PRD ("데이터 연동" section), controllers depend only on the abstract
SampleRepository / OrderRepository interfaces described here, so that a
real JSON-backed Repository can later be swapped in as a drop-in
replacement without touching controller code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from model.order import Order, OrderStatus
from model.sample import Sample


class SampleRepository(ABC):
    @abstractmethod
    def add(self, sample: Sample) -> None:
        ...

    @abstractmethod
    def get(self, sample_id: str) -> Optional[Sample]:
        ...

    @abstractmethod
    def list(self) -> list[Sample]:
        ...

    @abstractmethod
    def update(self, sample: Sample) -> None:
        ...

    @abstractmethod
    def find_by_name(self, keyword: str) -> list[Sample]:
        ...


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None:
        ...

    @abstractmethod
    def get(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def list(self) -> list[Order]:
        ...

    @abstractmethod
    def update(self, order: Order) -> None:
        ...

    @abstractmethod
    def list_by_status(self, status: OrderStatus) -> list[Order]:
        ...


class InMemorySampleRepository(SampleRepository):
    def __init__(self) -> None:
        self._samples: dict[str, Sample] = {}

    def add(self, sample: Sample) -> None:
        if sample.id in self._samples:
            raise ValueError(f"sample id already exists: {sample.id}")
        self._samples[sample.id] = sample

    def get(self, sample_id: str) -> Optional[Sample]:
        return self._samples.get(sample_id)

    def list(self) -> list[Sample]:
        return list(self._samples.values())

    def update(self, sample: Sample) -> None:
        if sample.id not in self._samples:
            raise ValueError(f"sample id not found: {sample.id}")
        self._samples[sample.id] = sample

    def find_by_name(self, keyword: str) -> list[Sample]:
        return [s for s in self._samples.values() if keyword in s.name]


class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def add(self, order: Order) -> None:
        if order.order_id in self._orders:
            raise ValueError(f"order id already exists: {order.order_id}")
        self._orders[order.order_id] = order

    def get(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def list(self) -> list[Order]:
        return list(self._orders.values())

    def update(self, order: Order) -> None:
        if order.order_id not in self._orders:
            raise ValueError(f"order id not found: {order.order_id}")
        self._orders[order.order_id] = order

    def list_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self._orders.values() if o.status == status]
