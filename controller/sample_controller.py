"""Controller for the '시료 관리' (sample management) menu.

Receives user input (already parsed into primitives by the caller),
validates/dispatches to the Model layer, and returns plain data
structures for the View to render. No console I/O happens here.
"""

from __future__ import annotations

from model.repository import SampleRepository
from model.sample import Sample


class SampleController:
    def __init__(self, sample_repository: SampleRepository) -> None:
        self._samples = sample_repository

    def register(
        self, sample_id: str, name: str, avg_production_time: float, yield_rate: float
    ) -> dict:
        sample = Sample(
            id=sample_id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock=0,
        )
        self._samples.add(sample)
        return sample.to_dict()

    def list_all(self) -> list[dict]:
        return [s.to_dict() for s in self._samples.list()]

    def search_by_name(self, keyword: str) -> list[dict]:
        return [s.to_dict() for s in self._samples.find_by_name(keyword)]
