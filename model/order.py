"""Order domain entity and status transition rules.

Field definitions and the status transition rules are sourced from the
shared schema document (../../../docs/SCHEMA.md) and the root PRD. This
module has no UI or storage dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OrderStatus(Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASE = "RELEASE"


# RESERVED -> CONFIRMED / PRODUCING / REJECTED
# PRODUCING -> CONFIRMED
# CONFIRMED -> RELEASE
_ALLOWED_TRANSITIONS = {
    OrderStatus.RESERVED: {OrderStatus.CONFIRMED, OrderStatus.PRODUCING, OrderStatus.REJECTED},
    OrderStatus.PRODUCING: {OrderStatus.CONFIRMED},
    OrderStatus.CONFIRMED: {OrderStatus.RELEASE},
    OrderStatus.REJECTED: set(),
    OrderStatus.RELEASE: set(),
}


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer_name: str
    quantity: int
    created_at: str
    status: OrderStatus = field(default=OrderStatus.RESERVED)

    def __post_init__(self) -> None:
        if not self.order_id:
            raise ValueError("order_id must not be empty")
        if not self.sample_id:
            raise ValueError("sample_id must not be empty")
        if not self.customer_name:
            raise ValueError("customer_name must not be empty")
        if self.quantity < 1:
            raise ValueError("quantity must be 1 or greater")

    def transition_to(self, new_status: OrderStatus) -> None:
        allowed = _ALLOWED_TRANSITIONS[self.status]
        if new_status not in allowed:
            raise ValueError(
                f"invalid status transition: {self.status.value} -> {new_status.value}"
            )
        self.status = new_status

    def to_dict(self) -> dict:
        return {
            "orderId": self.order_id,
            "sampleId": self.sample_id,
            "customerName": self.customer_name,
            "quantity": self.quantity,
            "status": self.status.value,
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        return cls(
            order_id=data["orderId"],
            sample_id=data["sampleId"],
            customer_name=data["customerName"],
            quantity=data["quantity"],
            created_at=data["createdAt"],
            status=OrderStatus(data["status"]),
        )
