"""Sample domain entity.

Field definitions are sourced from the shared schema document
(../../../docs/SCHEMA.md). This module has no UI or storage dependency.

Note: the schema field name "yield" is a reserved Python keyword, so the
in-memory attribute is named ``yield_rate``. Wire-format dicts (to_dict /
from_dict) still use the schema key "yield".
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Matches data-persistence's `_SAMPLE_ID_PATTERN` (docs/SCHEMA.md: "S-NNN"),
# so both modules reject the same malformed ids instead of console-mvc
# passing through ids that data-persistence would reject later.
_SAMPLE_ID_PATTERN = re.compile(r"^S-\d{3,}$")


@dataclass
class Sample:
    id: str
    name: str
    avg_production_time: float
    yield_rate: float
    stock: int

    def __post_init__(self) -> None:
        if not _SAMPLE_ID_PATTERN.match(self.id):
            raise ValueError(f"invalid sample id format: {self.id!r} (expected 'S-NNN')")
        if not self.name:
            raise ValueError("name must not be empty")
        if self.avg_production_time <= 0:
            raise ValueError("avg_production_time must be greater than 0")
        if not (0 < self.yield_rate <= 1):
            raise ValueError("yield_rate must satisfy 0 < yield_rate <= 1")
        if self.stock < 0:
            raise ValueError("stock must be 0 or greater")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "avgProductionTime": self.avg_production_time,
            "yield": self.yield_rate,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Sample":
        return cls(
            id=data["id"],
            name=data["name"],
            avg_production_time=data["avgProductionTime"],
            yield_rate=data["yield"],
            stock=data["stock"],
        )
